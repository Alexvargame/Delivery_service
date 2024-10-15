from .models import Street

def street_in_city(city,street):
     if not Street.objects.filter(city=city,name=street).exsists():
         raise forms.ValidationError(
             'Такой улицы нет в этом городе',
             params={'city': city,'name':street},
         )

