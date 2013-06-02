from django.shortcuts import *
from django.http import HttpResponse, HttpResponseRedirect
from kodare.iphone_sync.models import *
from datetime import datetime
from django.contrib.auth.models import User 
from django.db import transaction
from django import forms

def favicon(reques):
    return HttpResponse('')

def index(request):
    class LoginForm(forms.Form):
        email = forms.EmailField()
        code = forms.CharField(widget=forms.PasswordInput)
        
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            try:
                context = Context.objects.get(email=form.cleaned_data['email'], code=form.cleaned_data['code'])
                request.session['email'] = form.cleaned_data['email']
                request.session['code'] = form.cleaned_data['code']
                return HttpResponseRedirect('/')
            except Context.DoesNotExist:
                form.errors.append('incorrect email or code')
    elif 'code' in request.session and 'email' in request.session:
        context = Context.objects.get(email=request.session['email'], code=request.session['code'])
        objects = {}
        for o in ManagedObject.objects.filter(context=context).order_by('-data'):
            if o.decoded_data['category'] not in objects:
                objects[o.decoded_data['category']] = []
            objects[o.decoded_data['category']].append(o.decoded_data['text'])
        return render_to_response('iphone_sync/list.html', {'objects':objects})
    form = LoginForm(initial={})
    return render_to_response('iphone_sync/login.html', {'form':form})
 
@transaction.commit_on_success()
def sync(request):
    op = request.POST['operation']
    context, created = Context.objects.get_or_create(name=request.POST['context'], email=request.POST['email'])
    if created:
        context.code = User.objects.make_random_password()
        context.save()
        from django.core.mail import send_mail
        from django import template
        t = template.loader.get_template('new_sync_context_mail.html')                                         
        html_message = t.render(template.Context({'context':context, 'email':request.POST['email']}))
    
        from curia.html2text import html2text
        from curia.mail import send_html_mail_with_attachments
        text_message = html2text(html_message)
    
        from django.contrib.sites.models import Site
        send_html_mail_with_attachments(subject='New RandomNote synchronization account', message=text_message, html_message=html_message, from_email='no-reply@kodare.net', recipient_list=[request.POST['email']])
    entity = Entity.objects.get_or_create(name=request.POST['entity'])[0]
    objectURI = request.POST['objectURI']
    #print '"%s"' % request.POST['time'][:19]
    time = datetime.strptime(request.POST['time'][:19], '%Y-%m-%d %H:%M:%S')
    # TODO: handle time zone
    #time.timezone = request.POST['time'][-5:]

    #print context, entity, objectURI, time
    if op == 'delete':
        #print 'delete'
        try:
            ManagedObject.objects.get(context=context, entity=entity, objectURI=objectURI).delete()
        except ManagedObject.DoesNotExist:
            pass
    elif op == 'modify':
        data = request.POST['data']
        try:
            obj = ManagedObject.objects.get(context=context, entity=entity, objectURI=objectURI)
            #print 'modify existing'
            obj.modified = time
            obj.data = data
            obj.save()
        except ManagedObject.DoesNotExist:
            #print 'new object'
            ManagedObject.objects.create(context=context, entity=entity, objectURI=objectURI, data=data)
    #elif op == 'add'
    return HttpResponse('success')
