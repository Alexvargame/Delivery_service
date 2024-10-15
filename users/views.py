from django.shortcuts import render, redirect
from django.contrib import messages
from django import forms

from .forms import UserRegisterForm,ProfileForm,UserUpdateForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Profile, PhoneNumber
from .forms import PhoneWidget, PhoneNumberForm

def register(request):
    if request.method == 'POST':
        form=UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username=form.cleaned_data.get('username')
            messages.success(request, f'Ваш аккаунт создан')
            return redirect('login')
    else:
            form=UserRegisterForm()
    return render(request, 'users/register.html/',{'form':form})



@login_required
def profile(request):

    if len([ph.phone_number for ph in request.user.profile.phone_number.all()])<10:
        n=len([ph.phone_number for ph in request.user.profile.phone_number.all()])+1
    else:
        n=10
    numb=[]
    

    for user in User.objects.all():
        numb.extend([ph.phone_number for ph  in user.profile.phone_number.all() if user!=request.user])
    query_del=[]
    query=[(ph.phone_number,ph.phone_number) for ph  in request.user.profile.phone_number.all()]
    if request.method=='POST':
        
        u_form=UserUpdateForm(request.POST, instance=request.user)
        p_form=ProfileForm(request.POST,request.FILES,instance=request.user.profile)
        
        ph_form=PhoneNumberForm(request.POST)
        query_del=ph_form['phone_number'].value()
        new_ph_query=[ph.phone_number for ph  in request.user.profile.phone_number.all() if ph.phone_number not in query_del]

           
    
        if u_form.is_valid() and p_form.is_valid():# and ph_form.is_valid(): 
            u_form.save()
            pr=p_form.save()
            if ph_form['phone_number_add'].value():
                if ph_form['phone_number_add'].value() not in [ph.phone_number for ph in PhoneNumber.objects.all()]:
                    new_phone_number=PhoneNumber(phone_number=ph_form['phone_number_add'].value())
                    new_phone_number.save()
                    new_ph_query.append(ph_form['phone_number_add'].value())
                    pr.phone_number.set(PhoneNumber.objects.filter(phone_number__in=new_ph_query))
                    pr.save()
                    messages.success(request, f'Ваш профиль обновлен')
                    return redirect('profile')
                else:
                    if ph_form['phone_number_add'].value() not in numb:
                        new_ph_query.append(ph_form['phone_number_add'].value())
                        pr.phone_number.set(PhoneNumber.objects.filter(phone_number__in=new_ph_query))
                        pr.save()
                        messages.success(request, f'Ваш профиль обновлен')
                        return redirect('profile')
                    else:
                        messages.warning(request, f'Номер уже закреплен за другим пользователем')
            else:
                messages.success(request, f'Ваш профиль обновлен')
                return redirect('profile')
                    
            
           
                                
            
            
        else:
            messages.warning(request, f'Проверьте данные')
           
               
    else:
        u_form=UserUpdateForm(instance=request.user)
        p_form=ProfileForm(instance=request.user.profile)
        ph_form=PhoneNumberForm()
        

    context={
        'u_form':u_form,
        'p_form':p_form,
        #'ph_form':ph_form,
        #'s':request.user.get_user_permissions,
        #'s':(PhoneWidget(n).decompress(p_form['phone_number'].value()),p_form['phone_number'].value(),u_form['username'].value()),
        'phone_numbers':ph_form['phone_number'].as_widget(forms.CheckboxSelectMultiple(choices=query)),
        'phone_numbers_add':ph_form['phone_number_add'].as_widget(forms.TextInput()),
        'phone_number_list': request.user.profile.phone_number.all(),        
        }
            
    return render(request, 'users/profile.html',context=context)




def u(request):
    if request.POST.get('click', False):
        return render(request, 'users/1.html', context={'a':1})
    
