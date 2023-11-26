from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('home', views.home, name='home'),
    path('sign-up', views.sign_up, name='sign_up'),
    path('record/<int:record_id>/', views.detailed_view_record, name='detailed_view_record'),
    path('record/<int:record_id>/add_record/<str:test_type>/', views.add_record, name='add_record'),
    path('record/<int:record_id>/update_examinations/<uuid:diagnosis_id>/', views.update_examinations, name='update_examinations'),
    path('record/<int:record_id>/check_blood_test/', views.run_pkl_view, name='run_pkl_view'),
]