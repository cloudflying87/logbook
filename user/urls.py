from django.urls import path
from . import views
from .views import UpdatePreferences

urlpatterns = [
    path('', views.login_user, name="login_user"),
    path('user/<int:pk>/update/', UpdatePreferences.as_view(), name='updatepreferences'),
    # path('user/', UpdatePreferences.as_view(), name='updatepreferences'),
    path('user/logout', views.logout_user, name="logout_user"),
    path('user/create_user', views.create_user, name="create_user"),
]