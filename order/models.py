from django.db import models
from django.shortcuts import reverse
from django.contrib.auth.models import User

from random import randint
from datetime import datetime, timedelta

#from .validators import *

class City(models.Model):
    name=models.CharField(max_length=100)

    class Meta:
        verbose_name = 'Город'
        verbose_name_plural = 'Города'

    def __str__(self):
        return self.name
class Street(models.Model):
    name=models.CharField(max_length=100)
    city=models.CharField(choices=[(c.name,c.name) for c in City.objects.all()], max_length=100,blank=True,null=True)

    class Meta:
        verbose_name = 'Улица'
        verbose_name_plural = 'Улицы'
    def __str__(self):
        return f'{self.city}-{self.name}'

class Delivery_point(models.Model):
    name = models.CharField(max_length=100, blank=True, default='noname')
    city=models.CharField(choices=[(c.name,c.name) for c in City.objects.all()], max_length=100,blank=True)
    street=models.CharField(choices=list(set([(st.name, st.name) for st in Street.objects.all()])), max_length=100,blank=True)
    building=models.CharField(max_length=10,blank=True,null=True)
    office=models.CharField(max_length=10,blank=True,null=True,default=0)

    class Meta:
        verbose_name = 'Адрес доставки'
        verbose_name_plural = 'Адреса доставки'
    def __str__(self):
        return f"{self.name}, {self.city}, {self.street}, {self.building}, {self.office}"

    def get_absolute_url(self):
        return reverse('detail_delivery_point_url', kwargs={'pk': self.id})


    def get_sum_on_work_orders(self):
        return sum(list(ord.delivery_cost for ord in Order.objects.filter(delivery_point=self.id,delivery_status='on_work')))
    def get_count_on_work_orders(self):
        return list(ord for ord in Order.objects.filter(delivery_point=self.id,delivery_status='on_work'))
    def get_count_delivered_orders(self):
        return list(ord for ord in Order.objects.filter(delivery_point=self.id,delivery_status='delivered'))
    def get_sum_delivered_orders(self):
        return sum(list(ord.delivery_cost for ord in Order.objects.filter(delivery_point=self.id,delivery_status='delivered')))
    def get_count_canceled_orders(self):
        return list(ord for ord in Order.objects.filter(delivery_point=self.id,delivery_status='canceled'))
    def get_sum_canceled_orders(self):
        return sum(list(ord.delivery_cost for ord in Order.objects.filter(delivery_point=self.id,delivery_status='canceled')))
    def get_count_all_orders(self):
        return list(ord for ord in Order.objects.filter(delivery_point=self.id))
    def get_sum_all_orders(self):
        return sum(list(ord.delivery_cost for ord in Order.objects.filter(delivery_point=self.id)))
    def get_orderers(self):
        return list(set(ord.orderer for ord in Order.objects.filter(delivery_point=self.id)))



class Offices(models.Model):
    name=models.CharField(max_length=100,blank=True,default='noname')
    city=models.CharField(choices=[(c.name,c.name) for c in City.objects.all()], max_length=100,blank=True)
    street=models.CharField(choices=[(st.name, st.name) for st in Street.objects.all()], max_length=100,blank=True)
    building=models.CharField(max_length=10,blank=True,null=True)
    office=models.CharField(max_length=10,blank=True,null=True)

    class Meta:
        verbose_name = 'Адрес офиса'
        verbose_name_plural = 'Адреса офисов'
    def __str__(self):
        return f"{self.name}, {self.city}, {self.street}, {self.building}, {self.office}"

    def get_absolute_url(self):
        return reverse('detail_office_url', kwargs={'pk': self.id})

    def get_sum_on_work_orders(self):
        return sum(list(ord.delivery_cost for ord in Order.objects.filter(start_point=self.id,delivery_status='on_work')))
    def get_count_on_work_orders(self):
        return list(ord for ord in Order.objects.filter(start_point=self.id,delivery_status='on_work'))
    def get_count_delivered_orders(self):
        return list(ord for ord in Order.objects.filter(start_point=self.id,delivery_status='delivered'))
    def get_sum_delivered_orders(self):
        return sum(list(ord.delivery_cost for ord in Order.objects.filter(start_point=self.id,delivery_status='delivered')))
    def get_count_canceled_orders(self):
        return list(ord for ord in Order.objects.filter(start_point=self.id,delivery_status='canceled'))
    def get_sum_canceled_orders(self):
        return sum(list(ord.delivery_cost for ord in Order.objects.filter(start_point=self.id,delivery_status='canceled')))
    def get_count_all_orders(self):
        return list(ord for ord in Order.objects.filter(start_point=self.id))
    def get_sum_all_orders(self):
        return sum(list(ord.delivery_cost for ord in Order.objects.filter(start_point=self.id)))
    def get_orderers(self):
        return list(set(ord.orderer for ord in Order.objects.filter(start_point=self.id)))



class Order(models.Model):

    def get_delivery_cost(self):
        if float(self.delivery_cost)!=0:
            return float(self.delivery_cost)
        else:
            return randint(1,100)
    order_number=models.CharField(max_length=10,unique=True)
    deliver=models.ForeignKey(User, related_name='deliver', on_delete=models.DO_NOTHING, blank=True)
    orderer=models.ForeignKey(User,related_name='orderer',on_delete=models.DO_NOTHING,blank=True)
    start_point=models.ForeignKey(Offices,related_name='offices',on_delete=models.DO_NOTHING,default=Offices.objects.get(name='main').id)
    delivery_point=models.ForeignKey(Delivery_point,validators=[],related_name='delivery_points',on_delete=models.DO_NOTHING,default=1)
    delivery_cost=models.FloatField(default=0.0)
    description=models.TextField(blank=True)
    date_created=models.DateTimeField(auto_now_add=True)
    date_on_work=models.DateTimeField(default=datetime.now()+timedelta(minutes=30))
    date_finished=models.DateTimeField(default=datetime(2024,1,1,0,0))
    delivery_status=models.CharField(choices=[('waiting','waiting'),('on_work','on_work'),('delivered','delivered'),('canceled','canceled')],max_length=20,blank=True)

    class Meta:
        verbose_name='Заказ'
        verbose_name_plural='Заказы'

    def __str__(self):
        return f" {self.orderer}, {self.delivery_point}, {self.delivery_cost}, {self.description}"

    def get_absolute_url(self):
        return reverse('detail_order_url', kwargs={'pk': self.id})

    def get_update_url(self):
        return reverse('update_order_url', kwargs={'pk': self.id})

    def get_delete_url(self):
        return reverse('delete_order_url', kwargs={'pk': self.id})