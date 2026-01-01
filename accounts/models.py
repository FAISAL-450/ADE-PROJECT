from django.contrib.auth.models import User
from django.db import models
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    department = models.CharField(max_length=50, choices=[
        ('construction', 'Construction'),
        ('Finance', 'Finance'),
    ])
    def __str__(self):
        return f"{self.user.username} - {self.department}"
