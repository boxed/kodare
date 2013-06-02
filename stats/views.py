from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django import forms
from curia.shortcuts import *
from kodare.stats.models import *

@login_required
def index(request):
    class AddForm(forms.Form):
        category = forms.CharField()
        value = forms.CharField(required=True)
        
    if request.POST:
        form = AddForm(request.POST)
        if form.is_valid():
            try:
                category = Category.objects.get(user=request.user, name=form.cleaned_data['category'])
            except Category.DoesNotExist:
                category = Category.objects.create(user=request.user, name=form.cleaned_data['category'])
            entry = Entry.objects.create(category=category, value=form.cleaned_data['value'])
            return HttpResponseRedirect('/stats/')
    else:
        form = AddForm(initial={})
    return render_to_response(request, 'stats/index.html', {'form':form, 'categories':Category.objects.filter(user=request.user)})

@login_required    
def graph(request, category_name):
    return render_to_response(request, 'stats/graph.html')
