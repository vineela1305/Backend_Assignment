from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser):
    username = None
    name = models.CharField(max_length=100)
    email = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    dob = models.DateField()
    createdAt = models.DateTimeField(auto_now_add=True)
    modifiedAt = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'password', 'dob']

class Paragraph(models.Model):
    paragraph = models.TextField()
    createdAt = models.DateTimeField(auto_now_add=True)

class WordParagraphMapping(models.Model):
    paragraph = models.ForeignKey(Paragraph, on_delete=models.CASCADE, related_name='word_mappings')
    word = models.CharField(max_length=255)
    recurrence = models.IntegerField(default=0) 