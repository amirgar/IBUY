from django.db import models

class User(models.Model): 
    email = models.TextField(blank=True)
    password = models.TextField(blank=True)