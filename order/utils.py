from django import forms
from django.shortcuts import render, redirect
from django.views.generic import View
from django.shortcuts import get_object_or_404
from django.db.models import Q

from django.contrib.auth.models import User
from .models import Street,City,Order,Offices,Delivery_point
from django.contrib.auth.models import User,Permission, Group

from datetime import datetime,date,timedelta
from dateutil.tz import tzoffset

class AddressCreateMixin:
    form_model=None
    template=None
    def get(self, request):
        form=self.form_model()
        return render(request, self.template, context={'form':form})

    def post(self, request):
        bound_form=self.form_model(request.POST)
        if bound_form.is_valid():
            new_obj=bound_form.save()
            return redirect(new_obj)
        return render(request, self.template, context={'form':bound_form})


class AddressDetailMixin:
    model = None
    template = None
    def get(self, request, pk):
        obj = get_object_or_404(self.model, id=pk)
        return render(request, self.template, context={self.model.__name__.lower(): obj})

class AddressSearhMixin:
    form_model = None
    name_model = None
    template = None
    template_l = None
    initials = None

    def get(self,request):
        city_dict=[]
        street_dict=[]
        if request.GET:
            bound_form=self.form_model(request.GET)
            if bound_form['city'].value()!=['']:
                city_dict=bound_form['city'].value()
            else:
                for city in City.objects.all():
                    city_dict.append(city.name)
            if bound_form['street'].value()!=['']:
                street_dict=bound_form['street'].value()
            else:
                for st in Street.objects.all():
                    street_dict.append(st.name)
            if request.user.is_superuser:
                addresses=self.name_model.objects.filter(Q(name__icontains=request.GET['name'].lower())|Q(name__icontains=request.GET['name'].upper())|Q(name__icontains=request.GET['name'].capitalize()),
                                                 city__in=city_dict,street__in=street_dict)
            else:
                if self.name_model.__name__=='Delivery_point':
                    addresses = self.name_model.objects.filter(Q(name__icontains=request.GET['name'].lower()) | Q(name__icontains=request.GET['name'].upper()) | Q(
                            name__icontains=request.GET['name'].capitalize()),
                            city__in=city_dict, street__in=street_dict)
                    addresses=[ad for ad in addresses if ad in [ord.delivery_point for ord in Order.objects.filter(orderer=request.user)]]
                elif self.name_model.__name__=='Office':
                    addresses = self.name_model.objects.filter(Q(name__icontains=request.GET['name'].lower()) | Q(name__icontains=request.GET['name'].upper()) | Q(
                            name__icontains=request.GET['name'].capitalize()),
                            city__in=city_dict, street__in=street_dict)
                    addresses=[ad for ad in addresses if ad in [ord.delivery_point for ord in Order.objects.filter(deliver=request.user)]]

            return render(request,self.template,{self.name_model.__name__.lower()+'s':addresses})
        else:
            form = self.form_model(initial=self.initials)
            return render(request, self.template_l, {'form': form})


class SearchOrderDeliveryMixin:
    permission_required = 'order.view_order'
    initials=None
    form_model=None
    field=None
    template=None
    template_l=None
    group=None
    def check_choice(self,request,form, field, model):
        l=[]
        if form[field].value()!=[]:
            l=form[field].value()
        else:
            if field=='deliver':
                for obj in model.objects.filter(groups=Group.objects.get(name="Couriers")):
                    l.append(obj.id)
            elif field=='orderer':
                for obj in model.objects.all():
                    l.append(obj.id)
            else:
                for obj in model.objects.all():
                    l.append(obj.name)

        return l
    def get(self,request):
        if  request.user.is_superuser:
            if request.GET:
                deliver_dict = []
                orderer_dict = []
                status_dict = ['on_work','delivered','canceled']
                bound_form=self.form_model(request.GET,initial=self.initials)
                #print(bound_form['deliver'].value())
                deliver_dict=self.check_choice(request,bound_form,'deliver',User)
                orderer_dict=self.check_choice(request, bound_form, 'orderer', User)
                start_point_dict=[sp for sp in Offices.objects.filter(city__in=self.check_choice(request, bound_form, 'start_point_city', City),
                                                                      street__in=self.check_choice(request, bound_form, 'start_point_street', Street),
                                                                      name__in=self.check_choice(request, bound_form, 'start_point_name', Offices))]
                delivery_point_dict=[dp for dp in Delivery_point.objects.filter(city__in=self.check_choice(request, bound_form, 'delivery_point_city', City),
                                                                                street__in=self.check_choice(request, bound_form, 'delivery_point_street', Street))]
                if bound_form['delivery_status'].value()!=[]:
                    status_dict=bound_form['delivery_status'].value()
                date_b=[int(i) for i in request.GET['date_created_b'].split('-')]
                date_e=[int(i) for i in request.GET['date_created_e'].split('-')]

                objs=Order.objects.filter(Q(order_number__icontains=request.GET['order_number'].lower())|Q(order_number__icontains=request.GET['order_number'].upper())|Q(order_number__icontains=request.GET['order_number'].capitalize()),
                                            deliver__in=deliver_dict,orderer__in=orderer_dict,start_point__in=start_point_dict,
                                            delivery_point__in=delivery_point_dict,delivery_status__in=status_dict,
                                            delivery_cost__range=(bound_form['delivery_cost_min'].value(),bound_form['delivery_cost_max'].value()),
                                            date_created__range=(date(date_b[0],date_b[1],date_b[2]),date(date_e[0],date_e[1],date_e[2])))


                return render(request,self.template,{self.field+'s':objs})
            else:
                form=self.form_model(initial=self.initials)
                return render(request,self.template_l,{'form':form,
                     self.field:form[self.field].as_widget(forms.CheckboxSelectMultiple(choices=sorted([(obj.id, obj.username) for obj in User.objects.filter(groups=Group.objects.get(name=self.group))])))})
        else:
            if request.GET:
                deliver_dict = []
                status_dict = ['on_work', 'delivered', 'canceled']
                bound_form = self.form_model(request.GET, initial=self.initials)
                deliver_dict = self.check_choice(request, bound_form, 'deliver', User)
                orderer_dict = self.check_choice(request, bound_form, 'orderer', User)
                start_point_dict = [sp for sp in Offices.objects.filter(
                    city__in=self.check_choice(request, bound_form, 'start_point_city', City),
                    street__in=self.check_choice(request, bound_form, 'start_point_street', Street),
                    name__in=self.check_choice(request, bound_form, 'start_point_name', Offices))]
                delivery_point_dict = [dp for dp in Delivery_point.objects.filter(
                    city__in=self.check_choice(request, bound_form, 'delivery_point_city', City),
                    street__in=self.check_choice(request, bound_form, 'delivery_point_street', Street))]
                if bound_form['delivery_status'].value() != []:
                    status_dict = bound_form['delivery_status'].value()
                date_b = [int(i) for i in request.GET['date_created_b'].split('-')]
                date_e = [int(i) for i in request.GET['date_created_e'].split('-')]
                if self.field=='orderer':
                    objs = Order.objects.filter(Q(order_number__icontains=request.GET['order_number'].lower()) | Q(
                        order_number__icontains=request.GET['order_number'].upper()) | Q(
                        order_number__icontains=request.GET['order_number'].capitalize()),
                                                  deliver__in=deliver_dict, orderer=request.user,
                                                  start_point__in=start_point_dict,
                                                  delivery_point__in=delivery_point_dict, delivery_status__in=status_dict,
                                                  delivery_cost__range=(bound_form['delivery_cost_min'].value(),
                                                                        bound_form['delivery_cost_max'].value()),
                                                  date_created__range=(datetime(date_b[0], date_b[1], date_b[2]).replace(tzinfo=tzoffset(None,-7200)),
                                                                       ddatetime(date_e[0], date_e[1], date_e[2]).replace(tzinfo=tzoffset(None,-7200))))

                    return render(request, self.template, {self.field+'s': objs})
                elif self.field=='deliver':
                    objs = Order.objects.filter(Q(order_number__icontains=request.GET['order_number'].lower()) | Q(
                        order_number__icontains=request.GET['order_number'].upper()) | Q(
                        order_number__icontains=request.GET['order_number'].capitalize()),
                                                  orderer__in=orderer_dict, deliver=request.user,
                                                  start_point__in=start_point_dict,
                                                  delivery_point__in=delivery_point_dict, delivery_status__in=status_dict,
                                                  delivery_cost__range=(bound_form['delivery_cost_min'].value(),
                                                                        bound_form['delivery_cost_max'].value()),
                                                  date_created__range=(datetime(date_b[0], date_b[1], date_b[2]).replace(tzinfo=tzoffset(None, -7200)),
                                                                     ddatetime(date_e[0], date_e[1], date_e[2]).replace( tzinfo=tzoffset(None, -7200))))

                    return render(request, self.template, {self.field+'s': objs})
            else:
                form = self.form_model(initial=self.initials)
                return render(request, self.template_l, {'form': form,
                            self.field:form[self.field].as_widget(forms.CheckboxSelectMultiple(choices=[(request.user.id,request.user.username)]))})
class GroupListMixin:
    permission_required = 'users.view_user'
    group=None
    template=None
    field=None
    def get(self,request):
        group_dict={}
        group_users=User.objects.filter(groups=Group.objects.get(name=self.group))
        for us in group_users:
            if self.field=='deliver':
                key,value=us,Order.objects.filter(deliver=us)
                group_dict[key]=value
            elif self.field=='orderer':
                key, value = us, Order.objects.filter(orderer=us)
                group_dict[key] = value

        return render(request,self.template,{self.group.lower():group_users,self.group.lower()+'_dict':group_dict})

class ReportMixin:
    template=None
    field=None
    model_name=None
    model_form=None
    initials=None
    def get(self,request):
        if request.GET:
            result_dict={}
            objs=self.model_name.objects.all()
            bound_form=self.model_form(request.GET)
            date_b_ = [int(i) for i in request.GET['date_b'].split('-')]
            date_e_ = [int(i) for i in request.GET['date_e'].split('-')]
            print(objs)
            for obj in objs:
                if self.field=='start_point':
                    key,value=obj,Order.objects.filter(start_point=obj,delivery_status='delivered',
                        date_finished__range=(datetime(date_b_[0], date_b_[1], date_b_[2]).replace(tzinfo=tzoffset(None, -7200)),
                        datetime(date_e_[0], date_e_[1], date_e_[2]).replace(tzinfo=tzoffset(None, -7200))))
                elif self.field=='delivery_point':
                    key,value=obj,Order.objects.filter(delivery_point=obj,delivery_status='delivered',
                        date_finished__range=(datetime(date_b_[0], date_b_[1], date_b_[2]).replace(tzinfo=tzoffset(None, -7200)),
                        datetime(date_e_[0], date_e_[1], date_e_[2]).replace(tzinfo=tzoffset(None, -7200))))
                elif self.field=='deliver':
                    key, value = obj, Order.objects.filter(deliver=obj, delivery_status='delivered',
                    date_finished__range=(datetime(date_b_[0], date_b_[1], date_b_[2]).replace(tzinfo=tzoffset(None, -7200)),
                    datetime(date_e_[0], date_e_[1], date_e_[2]).replace(tzinfo=tzoffset(None, -7200))))
                elif self.field == 'orderer':
                    key, value = obj, Order.objects.filter(orderer=obj, delivery_status='delivered',date_finished__range=(
                    datetime(date_b_[0], date_b_[1], date_b_[2]).replace(tzinfo=tzoffset(None, -7200)),
                    datetime(date_e_[0], date_e_[1], date_e_[2]).replace(tzinfo=tzoffset(None, -7200))))
                if len(value)!=0:
                    value = [value, sum(v.delivery_cost for v in value)]
                    result_dict[key]=value

            return render(request,self.template,{'form':bound_form,'result_dict':result_dict})
        else:
            form=self.model_form(initial=self.initials)
            return render(request, self.template, {'form':form})
