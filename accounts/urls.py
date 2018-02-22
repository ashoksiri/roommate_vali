

from django.conf.urls import url
from .views import home,login_view,logout_view , register_view
from django.views.generic import RedirectView, TemplateView
from .views.rest_views import LoginView


urlpatterns = [

    url(r'^$',TemplateView.as_view(template_name='base.html')),
    url(r'^accounts/home/$',home,name='home'),
    url(r'^accounts/login/$',LoginView.as_view(),name='login'),
    url(r'^accounts/register/$',register_view,name='register'),
    url(r'^accounts/logout/$',logout_view,name='logout'),
    url(r'^accounts/forgot_password/$',TemplateView.as_view(template_name='roommate/password_reset.html'),name="forgot_password"),

]