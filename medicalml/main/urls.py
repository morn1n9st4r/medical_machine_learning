from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('home', views.home, name='home'),
    path('sign-up', views.sign_up, name='sign_up'),
    path('record/<int:record_id>/', views.detailed_view_record, name='detailed_view_record'),
    path('record/<int:record_id>/add_record/<str:test_type>/', views.add_record, name='add_record'),
]