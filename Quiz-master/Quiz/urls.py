from django.contrib import admin  
from django.urls import path, include  
from django.conf import settings  
from django.contrib.staticfiles.urls import staticfiles_urlpatterns  
from django.contrib.staticfiles.urls import static  

urlpatterns = [  
 path('admin/', admin.site.urls),  
 path('', include("App.urls")),  

]