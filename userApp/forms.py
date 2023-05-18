from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class DemoForm(forms.Form):
    name = forms.CharField(required=True)

class ApplicationForm(forms.Form): 
    name = forms.CharField(label='Name of Applicant', max_length=50) 
    address = forms.CharField(label='Address', max_length=100) 
    posts = (('Manager', 'Manager'),('Cashier', 'Cashier'),('Operator', 'Operator')) 
    field = forms.ChoiceField(choices=posts) 



class NewUserForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def save(self, commit=True):
        user = super(NewUserForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user