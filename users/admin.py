from django.contrib import admin


from .models import Profile, PhoneNumber

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display=('user','balance','status')
    

@admin.register(PhoneNumber)
class PhoneNumberAdmin(admin.ModelAdmin):
    list_display=('phone_number',)
