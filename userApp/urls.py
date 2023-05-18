from django.urls import path
from django.http import HttpResponse
from django.conf import settings
from django.conf.urls.static import static
from . import views
from djoser import views as djoser_views


urlpatterns = [
    path('', views.home, name='home'),
    path('home', views.home, name='home'),
    path('login/', views.login_view, name='login_user'),
    path('logout/', views.logout_view, name='logout_user'),
    path('api/auth/users/', views.create_user, name='user_create'),
    path('api/auth/logout/', views.logout_view, name='logout'),
    path('manager_dashboard/', views.manager_dashboard, name='manager_dashboard'),
]

if settings.DEBUG:
        urlpatterns += static(settings.MEDIA_URL,
                              document_root=settings.MEDIA_ROOT)
