import random

from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import View
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django import forms

from random import randint
from datetime import date,datetime,timedelta
import pytz
from dateutil.tz import tzoffset


from .models import Order,Offices,Delivery_point,City,Street
from .utils import AddressCreateMixin,AddressSearhMixin,SearchOrderDeliveryMixin,GroupListMixin,ReportMixin
from .validators import *
from django.contrib.auth.models import User,Permission, Group
from django.contrib.contenttypes.models import ContentType

from .forms import (OrderCreateForm,DeliveryCostCheckForm,SearchUserForm,
                    DeliveryPointForm,OfficeForm,SearchOfficeForm,
                    SearchOfficeForm,SearchDeliveryPointForm,OrderSearchForm,
                    DeliverListForm,DeliveryStatusForm,ReportDateForm)

from django.db.models import Q


def main_menu(request):
    return render(request,'order/main_page.html')

def main_admin_menu(request):
    return render(request,'order/main_admin_page.html')


class OrderCheckOnWork(PermissionRequiredMixin,View):
    permission_required = 'order.change_order'

    def post(self,request):
        for ord in Order.objects.filter(delivery_status='waiting'):
            t = ord.date_on_work + timedelta(hours=3)
            t = t.replace(tzinfo=None)
            print('t',t,'now',datetime.now())
            if t<datetime.now():
                ord.delivery_status='on_work'
                ord.save()
        return render(request,'order/main_admin_page.html',{'orders':Order.objects.all()})

class OrderCreateView(LoginRequiredMixin,PermissionRequiredMixin,View):
    permission_required = 'order.add_order'#request.user.get_all_permissions()

    def get_deliver(self):
        deliver_chouce={}
        for u in User.objects.filter(groups=Group.objects.get(name="Couriers")):
            key,value=u,len([ord for ord in Order.objects.select_related('deliver').filter(deliver=u)])
            if not key.is_superuser:
                deliver_chouce[key]=value
        return User.objects.get(id=random.choice([key.id for key in deliver_chouce.keys() if deliver_chouce[key] in sorted(list(deliver_chouce.values()))[:len(list(deliver_chouce.values()))//2+1]]))
    def get(self,request):
        number=str(randint(1,10000))
        form_delivery_point=DeliveryPointForm(initial={'building':0,'office':0})
        form=OrderCreateForm(initial={'orderer':request.user, 'deliver':[u for u in User.objects.filter(groups=Group.objects.get(name="Couriers"))][0],
                                      'order_number':number})
        return render(request,'order/create_order.html',{'form':form,'form_delivery_point':form_delivery_point})

    def post(self,request):
        number = str(randint(1, 10000))
        bound_form_delivery_point = DeliveryPointForm(request.POST,initial={'building':0,'office':0})
        bound_form=OrderCreateForm(request.POST)#,initial={'orderer':request.user,'deliver':[u for u in User.objects.filter(groups=Group.objects.get(name="Couriers"))][1],                                               #        'order_number':number})
        if bound_form.is_valid() and bound_form_delivery_point.is_valid():
            new_order=bound_form.save(commit=False)
            if Delivery_point.objects.filter(name=bound_form_delivery_point['name'].value(),city=bound_form_delivery_point['city'].value(),
                                             street=bound_form_delivery_point['street'].value(),building=bound_form_delivery_point['building'].value(),
                                             office=bound_form_delivery_point['office'].value()).exists():
                new_delivery_point=Delivery_point.objects.get(name=bound_form_delivery_point['name'].value(),city=bound_form_delivery_point['city'].value(),
                                             street=bound_form_delivery_point['street'].value(),building=bound_form_delivery_point['building'].value(),
                                             office=bound_form_delivery_point['office'].value())
            else:
                new_delivery_point=bound_form_delivery_point.save()
            new_order.delivery_point=new_delivery_point
            new_order.delivery_cost=bound_form['delivery_cost'].value()
            new_order.delivery_status='waiting'
            new_order.deliver=self.get_deliver()
            new_order.save()
            return redirect(new_order)


        return render(request,'order/create_order.html',{'form':bound_form,'form_delivery_point':bound_form_delivery_point,'message':f"Такой улицы в этом городе нет"})

class OrderCheckCreateView(LoginRequiredMixin,View):
        #permission_required = request.user.get_all_permissions()

        def get(self,request,cost,delivery_point_name,delivery_point_city,delivery_point_street,delivery_point_building,delivery_point_office):

            number=str(randint(1,10000))
            form=OrderCreateForm(initial={'orderer':request.user,'deliver':[u.id for u in User.objects.filter(groups=Group.objects.get(name="Couriers"))][0],
                                          #'deliver':Deliver.objects.get(id=1),
                                          'order_number':number,'delivery_cost':cost})
            form_delivery_point = DeliveryPointForm(initial={'name':delivery_point_name,'city':delivery_point_city,
                                                 'street':delivery_point_street,'building':delivery_point_building,
                                                 'office':delivery_point_office})

            return render(request,'order/create_order.html',{'form':form,'form_delivery_point':form_delivery_point})

class OrderUpdateView(LoginRequiredMixin,PermissionRequiredMixin,View):
    permission_required = 'order.change_order'
    def get(self,request,pk):
        order = Order.objects.get(id=pk)
        form_delivery_point = DeliveryPointForm(instance=order.delivery_point)
        form = OrderCreateForm(instance=order)

        if request.user.is_superuser:
            return render(request, 'order/update_order.html',
                          {'order': order, 'form': form, 'form_delivery_point': form_delivery_point})
        t = order.date_on_work + timedelta(hours=3)
        t = t.replace(tzinfo=None)
        if request.user in User.objects.filter(groups=Group.objects.get(name="Clients")) and t>datetime.now():
            return render(request,'order/update_order.html',{'order':order,'form':form,'form_delivery_point':form_delivery_point})
        else:
            return render(request, 'order/update_order.html', {'message':f"Вы не можете редактировать это заказ, он принят в работу"})
    def post(self,request,pk):
        number = str(randint(1, 10000))
        order = Order.objects.get(id=pk)
        bound_form_delivery_point = DeliveryPointForm(request.POST,instance=order.delivery_point)
        bound_form=OrderCreateForm(request.POST,instance=order)
        if bound_form.is_valid() and bound_form_delivery_point.is_valid():
            new_order=bound_form.save(commit=False)
            if Delivery_point.objects.filter(name=bound_form_delivery_point['name'].value(),city=bound_form_delivery_point['city'].value(),
                                             street=bound_form_delivery_point['street'].value(),building=bound_form_delivery_point['building'].value(),
                                             office=bound_form_delivery_point['office'].value()).exists():
                new_delivery_point=Delivery_point.objects.get(name=bound_form_delivery_point['name'].value(),city=bound_form_delivery_point['city'].value(),
                                             street=bound_form_delivery_point['street'].value(),building=bound_form_delivery_point['building'].value(),
                                             office=bound_form_delivery_point['office'].value())
            else:
                new_delivery_point=bound_form_delivery_point.save()
            new_order.delivery_point=new_delivery_point
            new_order.delivery_cost=bound_form['delivery_cost'].value()
            new_order.delivery_status='waiting'
            new_order.save()
            return redirect(new_order)


        return render(request,'order/update_order.html',{'form':bound_form,'form_delivery_point':bound_form_delivery_point})



class DeliveryDetailView(LoginRequiredMixin,View):

    def get(self,request,pk):
        if request.user.is_superuser:
            delivery=Order.objects.get(id=pk)
            return render(request,'order/detail_delivery.html',{'delivery':delivery})
        elif Order.objects.filter(id=pk,deliver=request.user).exists():
            delivery = Order.objects.get(id=pk, deliver=request.user)
            return render(request,'order/detail_delivery.html',{'delivery':delivery})
        return redirect(reverse('list_deliveres_url'))
class DeliveryUpdateView(LoginRequiredMixin,PermissionRequiredMixin,View):
    permission_required = 'order.change_order'
    def get(self,request,pk):
        delivery = Order.objects.get(id=pk)
        form=DeliveryStatusForm()
        return render(request,'order/update_delivery.html',{'delivery':delivery,'form':form})

    def post(self,request,pk):
        delivery = Order.objects.get(id=pk)
        bound_form = DeliveryStatusForm(request.POST)
        if bound_form.is_valid():
            delivery.delivery_status=bound_form['status'].value()
            delivery.date_finished=datetime.now()
            delivery.save()
            return redirect(reverse('list_deliveres_url'))

class OrderDetailView(LoginRequiredMixin,View):

    def get(self,request,pk):
        if request.user.is_superuser:
            order=Order.objects.get(id=pk)
            return render(request,'order/detail_order.html',{'order':order})
        elif Order.objects.filter(id=pk,orderer=request.user).exists():
            order = Order.objects.get(id=pk, orderer=request.user)
            return render(request,'order/detail_order.html',{'order':order})
        return redirect(reverse('list_orders_url'))

class OrderListView(PermissionRequiredMixin,View):
    permission_required = 'order.view_order'
    def get(self,request):
        form=DeliveryCostCheckForm()
        form_delivery_point=DeliveryPointForm(initial={'building':0,'office':0})
        if request.user.is_superuser:
            orders=Order.objects.all()
        else:
            orders=Order.objects.filter(orderer=request.user)
        context={
            'orders':orders,
            'form':form,
            'form_delivery_point':form_delivery_point,
            'summary':sum(ord.delivery_cost for ord in orders),

        }

        return render(request,'order/list_orders.html',context=context)


class DeliveryListView(PermissionRequiredMixin,View):
    permission_required = 'order.view_order'

    def check_waiting(self):
        for order in Order.objects.filter(delivery_status='waiting'):
                t = order.date_on_work + timedelta(hours=3)
                t = t.replace(tzinfo=None)#tzoffset(None, -7200))
                print('t', t, 'now', datetime.now(),t<datetime.now())
                if t < datetime.now():
                    order.delivery_status = 'on_work'
                    order.save()

    def get(self,request):
        self.check_waiting()
        delivery_dict=[]
        if request.user.is_superuser:
            if request.GET:
                form=DeliverListForm(request.GET)
                if form['deliver'].value()!=[]:
                    delivery_dict=form['deliver'].value()
                else:
                    for obj in User.objects.filter(groups=Group.objects.get(name="Couriers")):
                        delivery_dict.append(obj.id)
                deliveres_on_work= Order.objects.filter(deliver__in=delivery_dict,delivery_status='on_work')
                deliveres_delivered=Order.objects.filter(deliver__in=delivery_dict, delivery_status='delivered')
                deliveres_canceled=Order.objects.filter(deliver__in=delivery_dict, delivery_status='canceled')

                return render(request,'order/list_deliveres.html',{'form':form,'deliveres_on_work':deliveres_on_work,
                                                                   'deliveres_delivered':deliveres_delivered,
                                                                   'deliveres_canceled':deliveres_canceled,
                                                                   'summary_on_work':sum(ord.delivery_cost for ord in deliveres_on_work),
                                                                    'summary_delivered':sum(ord.delivery_cost for ord in deliveres_delivered),
                                                                   'summary_canceled': sum(ord.delivery_cost for ord in deliveres_canceled)
                                                                   })
            else:
                form=DeliverListForm()
                return render(request,'order/list_deliveres.html',{'form':form})
        else:
            deliveres_on_work = Order.objects.filter(deliver=request.user, delivery_status='on_work')
            deliveres_delivered = Order.objects.filter(deliver=request.user, delivery_status='delivered')
            deliveres_canceled = Order.objects.filter(deliver=request.user, delivery_status='canceled')

            return render(request, 'order/list_deliveres.html', {'deliveres_on_work': deliveres_on_work,
                                                                 'deliveres_delivered': deliveres_delivered,
                                                                 'deliveres_canceled': deliveres_canceled,
                                                                 'summary_on_work': sum(ord.delivery_cost for ord in deliveres_on_work),
                                                                 'summary_delivered': sum(ord.delivery_cost for ord in deliveres_delivered),
                                                                 'summary_canceled': sum(ord.delivery_cost for ord in deliveres_canceled)
                                                                 })
class OrderDeleteView(PermissionRequiredMixin,View):
    permission_required = 'order.delete_order'
    def get(self,request,pk):
        order= Order.objects.get(id=pk,orderer=request.user)
        return render(request, 'order/delete_order.html', context={'order': order})

    def post(self, request, pk):
        order = Order.objects.get(id=pk,orderer=request.user)
        order.delete()
        return redirect(reverse('list_orders_url'))

class OrderDoneView(LoginRequiredMixin,View):
    #def get(self,request,order):
     #   order= Order.objects.get(id=pk)
      #  return render(request, 'order/done_order.html', context={'order': order})

    def post(self, request,number):
        order = Order.objects.get(order_number=number,orderer=request.user)
        return redirect(order)

class DeliveryCostChekcView(View):
    def get(self,request):
        if request.GET:

            form_delivery_point=DeliveryPointForm(request.GET,initial={'building':0,'office':0})
            form=DeliveryCostCheckForm(request.GET,initial={'start_point':Offices.objects.get(name='main').id})
            context={'form': form, 'cost':0,'form_delivery_point': form_delivery_point,
             'delivery_point_name': form_delivery_point['name'].value(),
             'delivery_point_city': form_delivery_point['city'].value(),
             'delivery_point_street': form_delivery_point['street'].value(),
             'delivery_point_building': form_delivery_point['building'].value(),
             'delivery_point_office': form_delivery_point['office'].value(),
             }
            if form_delivery_point.is_valid():
                cost=randint(1,100)
                context['cost']=cost
                return render(request,'order/check_cost.html',context=context)
            context['message']= f"Такой улицы в этом городе нет"

            return render(request, 'order/check_cost.html',context=context)
        else:
            form_delivery_point=DeliveryPointForm(initial={'building':0,'office':0})
            form = DeliveryCostCheckForm(initial={'start_point': Offices.objects.get(name='main').id})
            return render(request, 'order/check_cost.html', {'form': form,'form_delivery_point':form_delivery_point})

class ClientsListView(PermissionRequiredMixin,GroupListMixin,View):
    permission_required = 'users.view_user'
    group = 'Clients'
    template = 'order/list_clients.html'
    field = 'orderer'

class CouriersListView(PermissionRequiredMixin,GroupListMixin,View):
    permission_required = 'users.view_user'
    group = 'Couriers'
    template = 'order/list_couriers.html'
    field = 'deliver'



class UsersSearchView(PermissionRequiredMixin,View):
    permission_required = 'users.view_user'

    def get(self,request,group_name):
        if request.GET:
            form=SearchUserForm(request.GET,initial={'groups':Group.objects.get(name=group_name).id})
            clients=User.objects.filter(Q(username__icontains=request.GET['username'].lower())|Q(username__icontains=request.GET['username'].upper())|Q(username__icontains=request.GET['username'].capitalize()),groups=request.GET['groups'])
            return render(request,'order/list_clients.html',{'clients':clients})
        else:
            form = SearchUserForm(initial={'groups':Group.objects.get(name=group_name).id})
            return render(request,'order/search_user.html',{'form':form})

class DeliveryPointCreateView(PermissionRequiredMixin,AddressCreateMixin,View):
    permission_required = 'order.add_delivery_point'
    form_model = DeliveryPointForm
    template = 'order/create_delivery_point.html'

class OfficeCreateView(PermissionRequiredMixin,AddressCreateMixin,View):
    permission_required = 'order.add_offices'
    form_model=OfficeForm
    template ='order/create_office.html'

class DeliveryPointDetailView(PermissionRequiredMixin,View):
    permission_required = 'order.view_delivery_point'

    def get(self,request,pk):

        if request.user.is_superuser or Delivery_point.objects.filter(id=pk,orderer=request.user).exists():
            dev_p_dict = {}
            dev_p=Delivery_point.objects.get(id=pk)
            context={'dev_p': dev_p,
                     'dev_p_dict':dev_p_dict,
                     }
            return render(request, 'order/detail_delivery_point.html', context=context)
        return redirect(reverse('list_delivery_points_url'))



class OfficeDetailView(PermissionRequiredMixin,View):
    permission_required = 'order.view_offices'
    def get(self,request,pk):
        office=Offices.objects.get(id=pk)
        return render(request,'order/detail_office.html',{'office':office})

class DeliveryPointListView(PermissionRequiredMixin,View):
    permission_required = 'order.view_delivery_point'
    def get(self,request):
        if request.user.is_superuser:
            dev_points=Delivery_point.objects.all()
        else:
            dev_points=[ord.delivery_point for ord in Order.objects.filter(orderer=request.user)]
        return render(request,'order/list_delivery_points.html',{'dev_points':dev_points})
class OfficesListView(PermissionRequiredMixin,View):
    permission_required = 'order.view_offices'
    def get(self,request):
        offices=Offices.objects.all()
        return render(request,'order/list_offices.html',{'offices':offices})

class SearchOfficeView(PermissionRequiredMixin,AddressSearhMixin,View):
    permission_required = 'order.view_offices'
    form_model = SearchOfficeForm
    name_model = Offices
    template = 'order/list_offices_search.html'
    template_l = 'order/search_office.html'
    initials = {'name':'','city':'','street':''}



class SearchDeliveryPointView(PermissionRequiredMixin,AddressSearhMixin,View):
    permission_required = 'order.view_delivery_point'
    form_model = SearchDeliveryPointForm
    name_model = Delivery_point
    template = 'order/list_delivery_points_search.html'
    template_l = 'order/search_delivery_point.html'
    initials = {'name':'','city':'','street':''}


class SearchOrderView(PermissionRequiredMixin,SearchOrderDeliveryMixin,View):
    permission_required = 'order.view_order'
    initials={'order_number':'','delivery_cost_min':0.00,'delivery_cost_max':10000.00,
              'date_created_b':date(2023,1,1),'date_created_e':date(2024,1,1)}
    form_model = OrderSearchForm
    field = 'orderer'
    template = 'order/list_orders_search.html'
    template_l = 'order/search_order.html'
    group = 'Clients'

class SearchDeliveryView(PermissionRequiredMixin,SearchOrderDeliveryMixin,View):
    permission_required = 'order.view_order'
    initials={'order_number':'','delivery_cost_min':0.00,'delivery_cost_max':10000.00,
              'date_created_b':date(2023,1,1),'date_created_e':date(2024,1,1)}
    form_model = OrderSearchForm
    field = 'deliver'
    template = 'order/list_deliveres_search.html'
    template_l = 'order/search_delivery.html'
    group = 'Couriers'

class ReportDeliveryPointsView(PermissionRequiredMixin,ReportMixin,View):
    permission_required = 'order.view_offices'
    initials={'date_b':date(2023,1,1),'date_e':datetime.now()}
    template ='order/report_delivery_points.html'
    field = 'delivery_point'
    model_name = Delivery_point
    model_form = ReportDateForm
class ReportOfficeView(PermissionRequiredMixin,ReportMixin,View):
    permission_required = 'order.view_offices'
    initials={'date_b':date(2023,1,1),'date_e':datetime.now()}
    template ='order/report_offices.html'
    field = 'start_point'
    model_name = Offices
    model_form = ReportDateForm

class ReportDeliverView(PermissionRequiredMixin,ReportMixin,View):
    permission_required = 'users.view_auth_user'
    initials = {'date_b': date(2023, 1, 1), 'date_e': datetime.now()}
    template = 'order/report_deliveres.html'
    field = 'deliver'
    model_name = User
    model_form = ReportDateForm

class ReportOrderersView(PermissionRequiredMixin,ReportMixin,View):
    permission_required = 'users.view_auth_user'
    initials = {'date_b': date(2023, 1, 1), 'date_e': datetime.now()}
    template = 'order/report_orderers.html'
    field = 'orderer'
    model_name = User
    model_form = ReportDateForm

class ReportAllOrdersView(PermissionRequiredMixin,View):
    permission_required = 'order.view_offices'
    initials={'date_b':date(2023,1,1),'date_e':datetime.now()}
    # def check_waiting(self):
    #     for ord in Order.objects.filter(delivery_status='waiting'):
    #             t = ord.date_on_work + timedelta(hours=3)
    #             t = t.replace(tzinfo=None)
    #             print('t', t, 'now', datetime.now())
    #             if t < datetime.now():
    #                 ord.delivery_status = 'on_work'
    #                 ord.save()
    def get(self,request):
        if request.GET:
            result_dict={}
            #('В ожидании', 'waiting'), ('В работе', 'on_work'),
            status=[('Доставленные','delivered'),('Отмененные','canceled')]
            #=Order.objects.all()
            bound_form=ReportDateForm(request.GET)
            date_b_ = [int(i) for i in request.GET['date_b'].split('-')]
            date_e_ = [int(i) for i in request.GET['date_e'].split('-')]
            # self.check_waiting()
            for st in status:
                key,value=st[0],Order.objects.filter(delivery_status=st[1],date_finished__range=(datetime(date_b_[0],
                            date_b_[1], date_b_[2]).replace(tzinfo=tzoffset(None, -7200)),
                            datetime(date_e_[0], date_e_[1], date_e_[2]).replace(tzinfo=tzoffset(None, -7200))))
                value=[value,sum(v.delivery_cost for v in value)]
                result_dict[key]=value
            return render(request,'order/report_all_orders.html',{'form':bound_form,'result_dict':result_dict})
        else:
            form=ReportDateForm(initial=self.initials)
            return render(request, 'order/report_all_orders.html', {'form':form})
