

from django.db import models
from django.forms import fields
from django.contrib.auth.models import User


class PhoneNumber(models.Model):
    phone_number=models.CharField(max_length=17, blank=True)#, primary_key=True)
    
    def __str__(self):
        return self.phone_number

    class Meta:
        verbose_name="Телефон"
        verbose_name_plural="Телефоны"


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_bot_id=models.IntegerField(blank=True,null=True,default=0)
    user_bot_pass=models.CharField(max_length=100,blank=True,null=True,default='')
    name=models.CharField(max_length=30, blank=True)
    sirname=models.CharField(max_length=30, blank=True)
    date_birth=models.DateField(null=True, blank=True)
    about_user=models.TextField(max_length=300, blank=True)
    phone_number=models.ManyToManyField(PhoneNumber,  verbose_name="Телефоны", related_name="phons")
    image = models.ImageField(default='default.jpg', upload_to='profile_pics')
    balance=models.DecimalField('Баланс',max_digits=10, decimal_places=2,default=0.00)
    status=models.CharField(max_length=100,choices=[('seller','seller'),('client','client'),('courier','courier')])
    

    def __str__(self):
        return f'{self.user.username} Profile'
    def get_phone_number(self):
       
        return [pn.phone_number for pn in self.phone_number.all()]
         

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)


##        img = Image.open(self.image.path)
##
##        if img.height > 300 or img.width > 300:
##            output_size = (300, 300)
##            img.thumbnail(output_size)
##            img.save(self.image.path)
