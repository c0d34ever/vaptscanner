from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('new/', views.new_scan, name='new_scan'),
    path('report/<int:scan_id>/', views.scan_report, name='scan_report'),
    path('playground/', lambda r: __import__('django').shortcuts.render(r, 'playground.html'), name='playground'),
    path('api/scans/', views.api_list_scans, name='api_list_scans'),
    path('api/scans/create/', views.api_create_scan, name='api_create_scan'),
    path('api/scans/<int:scan_id>/', views.api_get_scan, name='api_get_scan'),
]


