from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('custom_login_redirect/', views.custom_login_redirect, name='custom_login_redirect'),
    path('home', views.home, name='home'),
    path('sign-up', views.sign_up, name='sign_up'),
    path('record/<int:record_id>/', views.detailed_view_record, name='detailed_view_record'),
    path('record/<int:record_id>/edit_profile/', views.edit_record, name='edit_profile'),
    path('record/<int:record_id>/update_examinations/<uuid:diagnosis_id>/', views.update_examinations, name='update_examinations'),
    path('record/<int:record_id>/add_record/<str:test_type>/', views.add_record, name='add_record'),
    path('record/<int:record_id>/edit_record/<str:exam_type>/<uuid:id>/', views.edit_record, name='edit_record'),
    path('record/<int:record_id>/delete_record/<str:exam_type>/<uuid:id>/', views.delete_record, name='delete_record'),
    path('record/<int:record_id>/check_blood_test/', views.predict_blood_view, name='predict_blood_view'),
    path('record/<int:record_id>/check_thyroid_test/', views.predict_thyroid_view, name='predict_thyroid_view'),
]

