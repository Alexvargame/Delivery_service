from django.contrib import admin

from .models import *

@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(Street)
class StreetAdmin(admin.ModelAdmin):
    list_display = ('name',)



@admin.register(Delivery_point)
class Delivery_pointAdmin(admin.ModelAdmin):
    list_display = ('id','name','city','street','building','office')
@admin.register(Offices)
class OfficesAdmin(admin.ModelAdmin):
    list_display = ('id','name','city','street','building','office')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id',
    'order_number',
    'deliver',
    'orderer',
    'delivery_point',
    'delivery_cost',
    'description',
    'date_created',
    'date_on_work',
    'date_finished',
    'delivery_status')