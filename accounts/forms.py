from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
import unicodedata


class DateInput(forms.DateInput):
    input_type = 'date'

class SignUpForm(UserCreationForm):
    
    email   = forms.EmailField(
        label = "Enter Your Email Address",
        widget=forms.TextInput(attrs={'placeHolder':"Email Address" })
        )
    
    username = forms.CharField(
        label="User Name",
        widget=forms.TextInput(attrs={'placeHolder':"User Name" }))
    
    birth_date = forms.DateField(
        label="Birth Date",
        widget=forms.TextInput(attrs={'placeHolder':"Date of Birth eg@ dd/mm/yyyy"}),
    
    )

    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={'placeHolder':"Password" }))
    
    password2 = forms.CharField(
        label = "Repeat Password",
        widget=forms.PasswordInput(attrs={'placeHolder':"Repeat Password" }))

    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2','birth_date')

class UsernameField(forms.CharField):
    def to_python(self, value):
        return unicodedata.normalize('NFKC', super(UsernameField, self).to_python(value))
        

class LoginForm(forms.Form):
    
    """
    Base class for authenticating users. Extend this to get a form that accepts
    username/password logins.
    """
    
    error_messages = {
        'invalid_login': _(
            "Please enter a correct %(username)s and password. Note that both "
            "fields may be case-sensitive."
        ),
        'inactive': _("This account is inactive."),
    }
    

    username = UsernameField(
        max_length=254,
        widget=forms.TextInput(
            attrs={
                'class' : 'form-control p_input',
                'placeHolder':'Username',
                'autofocus': True}))
        
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={'class' : 'form-control p_input',
            'placeHolder':'Password'}))