from django.urls import path
from . import views

urlpatterns = [
    path('', views.get_email_credentials, name='get_email_credentials'),
    path('upload/', views.upload_file, name='upload_file'),
    path('map/', views.map_columns, name='map_columns'),
    path('logout/', views.logout_credentials, name='logout_credentials'),
    path('pricing/', views.pricing_view, name='pricing'),
    path('support/', views.support_view, name='support'),
    path('logs/', views.email_logs_view, name='email_logs'),  # ✅ New
  path('map/', views.map_columns, name='map_columns'),
    path('success/', views.success_page, name='success_page'),
  
]
