from rest_framework import serializers
from .models import User, Paragraph, WordParagraphMapping

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'password', 'dob']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    
    def create(self, validate_data):
        password = validate_data.pop('password', None)
        instance = self.Meta.model(**validate_data)
        if password is not None: 
            instance.set_password(password)
        instance.save()
        return instance
    
class ParagraphSerializer(serializers.ModelSerializer):
    class Meta:
        model = Paragraph
        fields = ['id', 'paragraph']

class WordParaMappingSerializer(serializers.ModelSerializer):
    class Meta:
        model = WordParagraphMapping
        fields = ['id', 'paragraph', 'word', 'recurrance']