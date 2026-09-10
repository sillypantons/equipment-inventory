from django.urls import path
from . import views

from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.equipment_list, name='equipment_list'),
    path('equipment/<str:SAGE_num>/', views.equipment_detail, name='equipment_detail'),
    path('equipment/<str:SAGE_num>/edit/', views.edit_equipment, name='edit_equipment'),
    path('equipment/<str:SAGE_num>/sign-in-out/', views.sign_in_out, name='sign_in_out'),
    path('equipment/<str:SAGE_num>/delete/', views.delete_equipment, name='delete_equipment'),
    path('equipment/<str:SAGE_num>/export/', views.export_equipment, name='export_equipment'),
    path('dashboard/', views.request_dashboard, name='request_dashboard'),
    path('dashboard/bulk-update/', views.bulk_update_requests, name='bulk_update_requests'),
    # path('dashboard/update/<int:request_id>/', views.update_request_status, name='update_request_status'),
    path('dashboard/update/<int:request_id>/<str:new_status>/', views.update_request_status, name='update_request_status'),
    path('dashboard/delete/<int:request_id>/', views.delete_request, name='delete_request'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('import/', views.import_equipment_view, name='import_equipment_view'),
]
