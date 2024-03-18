from django.contrib import admin
from .models import User, Paragraph, WordParagraphMapping

# Register your models here.
admin.site.register(User)
admin.site.register(Paragraph)
admin.site.register(WordParagraphMapping)