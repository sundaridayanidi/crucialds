"""crucialds URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from ingestapi import views

urlpatterns = [
    path(r'', views.index , name='viewproduct'),   
    path('admin/', admin.site.urls),
    path('addUser/',views.addUser, name='adduser'),
    path('updateRole/',views.updateRole, name='Updaterole'),
    path('addPDFHistory/',views.addPDFHistory, name='AddPDFHistory'),
    path('addEDCSubmission/',views.addEDCSubmission, name='AddEDCsubmission'),
    path('getSettings/',views.getSettings, name='getSettings'),
    path('logIP/',views.logIP, name='logIP'),
    path('getTimeline/',views.getTimeline, name='getTimeline'),
    path('insert/',views.insert, name='insert'),
    path('delete/',views.delete, name='delete'),
   # path('costing/',views.costing, name='costing'),
    #path('readmissions/',views.readmissions, name='readmissions'),
    #path('linkback/',views.linkback, name='linkback'),
    #path('distribution/',views.distribution, name='distribution'),
    #path('countdistribution/',views.countdistribution, name='countdistribution'),
]
