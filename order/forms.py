from django import forms
from django_select2 import forms as s2forms
from django.forms import widgets, fields

from .models import Order,Delivery_point,Offices,Street,City
from users.models import Profile
from django.contrib.auth.models import User, Group

class AddressWidget(s2forms.ModelSelect2Widget):
    search_fields = ['name__incontains']
class OrderCreateForm(forms.ModelForm):

    class Meta:
        model=Order
        fields=['order_number','deliver','orderer','delivery_point','description','delivery_cost']
        widgets={
            'delivery_point':forms.Select(attrs={'class':'form-control'}),
            'desciption':forms.TextInput(attrs={'class':'form-control', 'empty_value':True})
        }




class DeliveryCostCheckForm(forms.ModelForm):

    class Meta:
        model=Order
        fields=['start_point']
        widgets={
            #'delivery_point':forms.Select(attrs={'class':'form-control'}),
            'start_point':forms.Select(attrs={'class':'form-control'})
        }

class SearchUserForm(forms.ModelForm):

    class Meta:
        model=User
        fields=['username','groups']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'empty_value':True}),
            'groups': forms.TextInput(attrs={'class': 'form-control', 'empty_value': True}),

        }

class DeliveryPointForm(forms.ModelForm):

    class Meta:
        model=Delivery_point
        fields=['name','city','street','building','office']
        widgets={
            'name': forms.TextInput(attrs={'class': 'form-control', 'empty_value': True}),
            'city': forms.Select(attrs={'class': 'form-control', 'empty_value': True}),
            'street': forms.Select(attrs={'class': 'form-control', 'empty_value': True}),
            'building': forms.TextInput(attrs={'class': 'form-control', 'empty_value': True}),
            'office': forms.TextInput(attrs={'class': 'form-control', 'empty_value': True}),
        }
    def clean_street(self):
        data=self.cleaned_data['street']
        data_city=self.cleaned_data['city']
        if not Street.objects.filter(city=data_city, name=data).exists():

            raise forms.ValidationError(
                'Такой улицы нет в этом городе!'
            )

        return data

class OfficeForm(forms.ModelForm):

    class Meta:
        model=Offices
        fields=['name','city','street','building','office']
        widgets={
            'name': forms.TextInput(attrs={'class': 'form-control', 'empty_value': True}),
            'city': forms.Select(attrs={'class': 'form-control', 'empty_value': True}),
            'street': forms.Select(attrs={'class': 'form-control', 'empty_value': True}),
            'building': forms.TextInput(attrs={'class': 'form-control', 'empty_value': True}),
            'office': forms.TextInput(attrs={'class': 'form-control', 'empty_value': True}),
        }

class SearchOfficeForm(forms.ModelForm):

    class Meta:
        model=Offices
        fields=['name','city','street']
        widgets={
            'name': forms.TextInput(attrs={'class': 'form-control', 'empty_value': True}),
            'city': forms.SelectMultiple(attrs={'class': 'form-control', 'empty_value': True}),
            'street': forms.SelectMultiple(attrs={'class': 'form-control', 'empty_value': True}),
        }

class SearchDeliveryPointForm(forms.ModelForm):

    class Meta:
        model=Delivery_point
        fields=['name','city','street']
        widgets={
            'name': forms.TextInput(attrs={'class': 'form-control', 'empty_value': True}),
            'city': forms.SelectMultiple(attrs={'class': 'form-control', 'empty_value': True}),
            'street': forms.SelectMultiple(attrs={'class': 'form-control', 'empty_value': True}),
        }

class SearchDeliveryPointForm(forms.ModelForm):

    class Meta:
        model=Delivery_point
        fields=['name','city','street']
        widgets={
            'name': forms.TextInput(attrs={'class': 'form-control', 'empty_value': True}),
            'city': forms.SelectMultiple(attrs={'class': 'form-control', 'empty_value': True}),
            'street': forms.SelectMultiple(attrs={'class': 'form-control', 'empty_value': True}),
        }



class OrderSearchForm(forms.Form):

    order_number=forms.CharField(required=False,widget=forms.TextInput(attrs={'class': 'form-control', 'empty_value': True}))
    deliver=forms.CharField(label='Доставщик',
                               widget=forms.CheckboxSelectMultiple(
                                   choices=sorted([(obj.id, obj.username) for obj in User.objects.filter(groups=Group.objects.get(name="Couriers"))])))

    orderer=forms.CharField(label='Заказчик',
                               widget=forms.CheckboxSelectMultiple(
                                   choices=sorted([(obj.id, obj.username) for obj in User.objects.filter(groups=Group.objects.get(name="Clients"))])))


    start_point_name = forms.CharField(label='Название  офиса',
                                   widget=forms.CheckboxSelectMultiple(
                                       choices=sorted([(obj.name, obj.name) for obj in Offices.objects.all()])))
    start_point_city=forms.CharField(label='Город офиса',
                               widget=forms.CheckboxSelectMultiple(
                                   choices=sorted([(obj.name, obj.name) for obj in City.objects.all()])))
    start_point_street = forms.CharField(label='Улица офиса',
                                       widget=forms.CheckboxSelectMultiple(
                                           choices=sorted([(obj.name, obj.name) for obj in Street.objects.all()])))
    delivery_point_city = forms.CharField(label='Город адреса',
                                       widget=forms.CheckboxSelectMultiple(
                                           choices=sorted([(obj.name, obj.name) for obj in City.objects.all()])))
    delivery_point_street = forms.CharField(label='Улица адреса',
                                         widget=forms.CheckboxSelectMultiple(
                                             choices=sorted([(obj.name, obj.name) for obj in Street.objects.all()])))
    date_created_b = forms.DateField(label='начальная дата', widget=forms.DateInput(
        attrs={'class': 'form-control', 'empty_value': True, 'type': 'date'}))
    date_created_e = forms.DateField(label='конечная дата', widget=forms.DateInput(
        attrs={'class': 'form-control', 'empty_value': True, 'type': 'date'}))
    delivery_cost_min=forms.FloatField(widget=forms.NumberInput(attrs={'class': 'form-control', 'empty_value': True}))
    delivery_cost_max = forms.FloatField(widget=forms.NumberInput(attrs={'class': 'form-control', 'empty_value': True}))

    delivery_status = forms.CharField(label="Статус исполнения",
                             widget=forms.CheckboxSelectMultiple(choices=[('on_work', 'on_work'), ('delivered','delivered'),('canceled','canceled')]))

class DeliverListForm(forms.Form):
    deliver = forms.CharField(label='Доставщик',
                              widget=forms.CheckboxSelectMultiple(
                                  choices=sorted([(obj.id, obj.username) for obj in
                                                  User.objects.filter(groups=Group.objects.get(name="Couriers"))])))


class DeliveryStatusForm(forms.Form):
    status = forms.CharField(label='Доставщик',
                              widget=forms.Select(
                                  choices=sorted([('delivered','delivered'),('canceled','canceled')])))
class ReportDateForm(forms.Form):
    date_b = forms.DateTimeField(label='начальная дата', widget=forms.DateInput(
        attrs={'class': 'form-control', 'empty_value': True, 'type': 'date'}))
    date_e = forms.DateTimeField(label='конечная дата', widget=forms.DateInput(
        attrs={'class': 'form-control', 'empty_value': True, 'type': 'date'}))
