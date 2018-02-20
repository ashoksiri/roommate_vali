from django.conf.urls import url,include
from django.contrib import admin
from django.views.generic import TemplateView
from .views import home,login_view,logout_view , register , profile , mail,analysis
from django.views.generic import RedirectView, TemplateView
from rest_framework.routers import DefaultRouter
from .views.rest_views import UsersView

router = DefaultRouter()

#router.register('register',UsersView,base_name='register')


urlpatterns = [
    #url(r'^accounts/register/$',UsersView.as_view(),name='register'),
    #url(r'^accounts/',include(router.urls))
    url(r'^$',RedirectView.as_view(url='accounts/home')),
    url(r'^accounts/home/$',home,name='home'),
    url(r'^accounts/login/$',login_view,name='login'),
    url(r'^accounts/register/$',register,name='register'),
    url(r'^accounts/logout/$',logout_view,name='logout'),
    url(r'^accounts/forgot_password/$',TemplateView.as_view(template_name='roommate/password_reset.html'),name="forgot_password"),
    url(r'^accounts/profile/$',profile,name="profile"),
    url(r'^accounts/charts/$',analysis,name="charts"),
    url(r'^accounts/mail/$',mail,name="mail"),

]