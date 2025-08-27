from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('new/', views.new_scan, name='new_scan'),
    path('report/<int:scan_id>/', views.scan_report, name='scan_report'),
    path('playground/', lambda r: __import__('django').shortcuts.render(r, 'playground.html'), name='playground'),
    
    # Core API endpoints
    path('api/scans/', views.api_list_scans, name='api_list_scans'),
    path('api/scans/create/', views.api_create_scan, name='api_create_scan'),
    path('api/scans/<int:scan_id>/', views.api_get_scan, name='api_get_scan'),
    path('api/scans/<int:scan_id>/logs/', views.api_scan_logs, name='api_scan_logs'),
    path('api/test/', views.api_test, name='api_test'),
    
    # Enhanced features
    path('api/templates/', views.api_list_templates, name='api_list_templates'),
    path('api/templates/create/', views.api_create_template, name='api_create_template'),
    path('api/scheduled/', views.api_list_scheduled_scans, name='api_list_scheduled_scans'),
    path('api/scheduled/create/', views.api_create_scheduled_scan, name='api_create_scheduled_scan'),
    path('api/bulk-scan/', views.api_bulk_scan, name='api_bulk_scan'),
    path('api/stats/', views.api_scan_stats, name='api_scan_stats'),
    path('api/scans/<int:scan_id>/export/', views.api_export_scan, name='api_export_scan'),
    path('api/search/', views.api_search_scans, name='api_search_scans'),
]


