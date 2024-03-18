from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from .serializers import UserSerializer, ParagraphSerializer, WordParaMappingSerializer
from .models import User, Paragraph, WordParagraphMapping
import jwt, datetime
from collections import Counter
from django.db.models import Sum, F

# Create your views here.
class AuthenticationMixin:
    def authenticate_request(self, request):
        token = request.COOKIES.get('jwt')

        if not token:
            raise AuthenticationFailed('Unauthenticated!')

        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated!')
        except jwt.DecodeError:
            raise AuthenticationFailed('Invalid token!')

        user = User.objects.filter(id=payload['id']).first()
        if user is None:
            raise AuthenticationFailed('User not found!')

        return user

class RegisterView(APIView):
    def post(self, request):
        serialiser = UserSerializer(data=request.data)
        serialiser.is_valid(raise_exception=True)
        serialiser.save()
        return Response(serialiser.data)
    
class LoginView(APIView):
    def post(self, request):
        email = request.data['email']
        password = request.data['password']

        user = User.objects.filter(email=email).first()

        if user is None:
            raise AuthenticationFailed('User not found!')
        
        if not user.check_password(password):
            raise AuthenticationFailed("Incorrect Password!")
        
        payload = {
            'id': user.id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
            'iat': datetime.datetime.utcnow()
        }

        token = jwt.encode(payload, 'secret', algorithm='HS256')

        response = Response()

        response.set_cookie(key='jwt', value=token, httponly=True)
        response.data = {
            'jwt': token
        }

        return response

class UserView(APIView, AuthenticationMixin):
    def get(self, request):
        user = self.authenticate_request(request)
        serialiser = UserSerializer(user)
        return Response(serialiser.data)
    
class LogoutView(APIView):
    def post(self, request):
        response = Response()
        response.delete_cookie('jwt')
        response.data = {
            'message': 'success'
        }
        return response

class ParagraphView(APIView, AuthenticationMixin):
    def post(self, request):
            user = self.authenticate_request(request)
            data = request.data
            paragraphs = data.get('paragraphs', '').split('\n\n')
            for paragraph_text in paragraphs:
                paragraph, _ = Paragraph.objects.get_or_create(paragraph=paragraph_text)
                word_counts = Counter(word.lower() for word in paragraph_text.split())
                for word, count in word_counts.items():
                    word_mapping, created = WordParagraphMapping.objects.get_or_create(
                    word=word, 
                    paragraph=paragraph,
                    defaults={'recurrence': count}
                )
                if not created:
                    # If the mapping already exists, update the recurrence count.
                    # This is just an example. Adjust based on how you want to handle recurrences.
                    word_mapping.recurrence = F('recurrence') + count
                    word_mapping.save(update_fields=['recurrence'])
            return Response({"message": "Paragraphs stored successfully"}, status=201)

class SearchView(APIView, AuthenticationMixin):
    def get(self, request):
        user = self.authenticate_request(request)
        
        word = request.query_params.get('word', '').lower()
        
        mappings = WordParagraphMapping.objects \
            .filter(word=word) \
            .values('paragraph') \
            .annotate(total_recurrence=Sum('recurrence')) \
            .order_by('-total_recurrence')[:10]
        
        paragraph_ids = [mapping['paragraph'] for mapping in mappings]
        paragraphs_in_order = {p.id: p for p in Paragraph.objects.filter(id__in=paragraph_ids)}
        sorted_paragraphs = [paragraphs_in_order[pid] for pid in paragraph_ids if pid in paragraphs_in_order]
        
        # Serialize and return the paragraphs
        paragraph_data = ParagraphSerializer(sorted_paragraphs, many=True).data
        return Response({"paragraphs": paragraph_data}, status=200)