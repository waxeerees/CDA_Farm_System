from django.urls import path
from django.http import HttpResponse
from django.conf import settings
from django.conf.urls.static import static
from . import views
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path('groups/manager/users', views.managers),
]