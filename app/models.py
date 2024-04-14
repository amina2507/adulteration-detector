from django.contrib import admin
from django.db import models
from django.contrib.auth.models import User



class Registration(models.Model):
    First_name = models.CharField(max_length=200)
    Last_name = models.CharField(max_length=200)
    Email = models.EmailField(max_length=200,  null=True)
    Mobile_Number = models.CharField(max_length=20) 
    Password = models.CharField(max_length=200)
    Registration_date = models.DateField()
    User_role = models.CharField(max_length=200)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)


    def __str__(self):
        return self.First_name
    


class Feedback(models.Model):
    registration = models.ForeignKey(Registration, on_delete=models.CASCADE) 
    comments = models.CharField(max_length=200)
    rating = models.IntegerField(default=0)



class images(models.Model):
    user_name = models.CharField(max_length=50)
    image = models.CharField(max_length=50)  # Assuming you want to store the image data as a binary field
    date_created = models.DateTimeField(auto_now_add=True)
    result=models.CharField(max_length=200)
