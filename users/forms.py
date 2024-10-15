from django import forms
from django.shortcuts import render, redirect

from django.forms import fields, widgets
from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile, PhoneNumber





class PhoneWidget(forms.MultiWidget):
    def __init__(self,n,attrs=None):

        widgets=[forms.TextInput(attrs={'size':20,'class':'form-control', 'empty_value':True, 'initial':''})]*n
        
        super().__init__(widgets, attrs)


    def decompress(self, value):
        numbs=PhoneNumber.objects.filter(id__in=value)
        nums=[ph.phone_number for ph in numbs]
        return nums
    
 

class PhoneField(fields.MultiValueField):
    def __init__(self,*args, **kwargs):
        list_phones=[models.CharField()]*5
        super(PhoneField,self).__init__(list_phones,  widget=PhoneWidget(), *args, **kwargs)        

    def compress(self, values):
        return values




    
class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

        
class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email']
     

##class ProfileForm(forms.ModelForm):
##
##    class Meta:
##        model=Profile
##        fields=['name','sirname','date_birth','about_user','phone_number', 'image']
##        widgets={
##            'name':forms.TextInput(attrs={'class':'form-control', 'empty_value':True}),# 'disabled':True}),
##            'sirname':forms.TextInput(attrs={'class':'form-control', 'empty_value':True}),
##            'date_birth':forms.DateInput(attrs={'class':'form-control', 'empty_value':True, 'type':'date'}),
##            'about_user':forms.Textarea(attrs={'class':'form-control', 'empty_value':True}),
##            'phone_number':PhoneWidget(n=10),
##            'image':forms.ClearableFileInput(attrs={'class':'form-control', 'empty_value':True}),
##            }
##


class ProfileForm(forms.ModelForm):
    class Meta:
        model=Profile
        fields=['name','sirname','date_birth','about_user','image']
        widgets={
            'name':forms.TextInput(attrs={'class':'form-control', 'empty_value':True}),
            'sirname':forms.TextInput(attrs={'class':'form-control', 'empty_value':True}),
            'date_birth':forms.DateInput(attrs={'class':'form-control', 'empty_value':True, 'type':'date'}),
            'about_user':forms.Textarea(attrs={'class':'form-control', 'empty_value':True}),
            'image':forms.ClearableFileInput(attrs={'class':'form-control', 'empty_value':True}),
            }
class PhoneNumberForm(forms.Form):
    
    phone_number=forms.CharField(widget=forms.CheckboxSelectMultiple(choices=[],
                                    attrs={'class':'form-control','empty_value':True}))
    phone_number_add=forms.CharField(widget=forms.TextInput(attrs={'class':'form-control','empty_value':True}),required=False)
    
   
                 
class ProfileUpdateForm(forms.ModelForm):
    class Meta:
    	model = Profile
    	fields = ['image']

    	widgets={
            
            'image':forms. ClearableFileInput(attrs={'class':'form-control', 'empty_value':True}),
            }
