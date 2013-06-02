from curia.shortcuts import *
from curia import *
from curia.html2text import html2text
from curia.mail import send_html_mail_with_attachments
from curia.forms import SplitDateTimeWidget2
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.forms import ModelForm
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.sites.models import Site
from django.template import loader, Context
from kodare.countdown.models import *
from datetime import datetime

class CountdownForm(ModelForm):
     class Meta:
         model = Countdown
CountdownForm.base_fields['target_time'].widget = SplitDateTimeWidget2()

def index(request):
    return render_to_response(request, 'countdown/index.html')
    
def create_countdown(request):
    if request.method == 'POST':
        form = CountdownForm(request.POST)
        if form.is_valid():
            countdown = form.save()
            countdown.password = User.objects.make_random_password(5)
            countdown.save()
            
            # mail creator
            c = {
                'countdown': countdown,
                'url': 'http://%s%s' % (Site.objects.get_current().domain, countdown.get_absolute_url()),
            }
            html_message = loader.get_template('countdown/created_email.html').render(Context(c))

            text_message = html2text(html_message)
            send_html_mail_with_attachments(subject=_('Countdown created'), message=text_message, html_message=html_message, from_email='robot@'+Site.objects.get_current().domain, recipient_list=[countdown.creator])
            
            return HttpResponseRedirect(countdown.get_absolute_url())
    else:
        now = datetime.now()
        form = CountdownForm(initial={'target_time':datetime(now.year, now.month, now.day)})
        
    return render_to_response(request, 'countdown/create.html', {'form':form})

def view_countdown(request, countdown_id):
    return render_to_response(request, 'countdown/view_countdown.html', {'countdown':Countdown.objects.get(pk=countdown_id)})

def edit_countdown(request, countdown_id):
    countdown = Countdown.objects.get(pk=countdown_id)
    if countdown.password != request.REQUEST['password']:
        return render_to_response(request, 'countdown/access_denied.html')
        
    if request.method == 'POST':
        form = CountdownForm(request.POST, instance=countdown)
        if form.is_valid():
            countdown = form.save()
            
            # mail creator
            c = {
                'countdown': countdown,
                'url': 'http://%s%s' % (Site.objects.get_current().domain, countdown.get_absolute_url()),
            }
            html_message = loader.get_template('countdown/created_email.html').render(Context(c))

            text_message = html2text(html_message)
            send_html_mail_with_attachments(subject=_('Countdown created'), message=text_message, html_message=html_message, from_email='robot@'+Site.objects.get_current().domain, recipient_list=[countdown.creator])
            
            return HttpResponseRedirect(countdown.get_absolute_url())
    else:
        form = CountdownForm(instance=countdown)
        
    return render_to_response(request, 'countdown/edit_countdown.html', {'form':form})

def add_notification(request, countdown_id):
    pass
