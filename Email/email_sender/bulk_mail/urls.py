from django.urls import path
from . import views

urlpatterns = [
    path('', views.get_email_credentials, name='get_email_credentials'),
    path('upload/', views.upload_file, name='upload_file'),
    path('map/', views.map_columns, name='map_columns'),
    path('logout/', views.logout_credentials, name='logout_credentials'),

]
