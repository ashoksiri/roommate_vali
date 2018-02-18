"""roommate URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url,include
from django.contrib import admin
from django.contrib.staticfiles.urls import  staticfiles_urlpatterns

from django.views.generic import TemplateView , RedirectView
from accounts import views as account_views
from django.contrib.auth import views as auth_views



urlpatterns = [

    url(r'',include('accounts.urls')),
    url(r'^$',TemplateView.as_view(template_name='login.html'),name='login'),
    url(r'^admin/', admin.site.urls),

    # url(r'^oauth/', include('social_django.urls', namespace='social')),  # <--
    # url(r'^$', account_views.home, name='home'),
    # url(r'^accounts/logout/$', auth_views.logout, {'next_page': 'login'}, name='logout'),
    # url(r'^signup/$', account_views.signup, name='signup'),

] + staticfiles_urlpatterns()


handler404 = 'roommate.views.handler404'
handler500 = 'roommate.views.handler500'