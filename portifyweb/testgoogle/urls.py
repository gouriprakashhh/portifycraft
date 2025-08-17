from django.urls import path
from . import views

urlpatterns = [
    path('editor', views.testdata, name='generate_page'),
    # urls.py
path('upload-image/', views.upload_image, name='upload_image'),
 path('projects/manage/', views.manage_content_view, name='project_manage'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    
    # API endpoints
    path('save_personal_details/', views.save_personal_details, name='save_personal_details'),
    path('save_contact_info/', views.save_contact_info, name='save_contact_info'),
    path('add_project/', views.add_project, name='add_project'),
    path('update_project/<int:project_id>/', views.update_project, name='update_project'),
    path('delete_project/<int:project_id>/', views.delete_project, name='delete_project'),
    path('add_skill/', views.add_skill, name='add_skill'),
    path('update_skill/<int:skill_id>/', views.update_skill, name='update_skill'),
    path('delete_skill/<int:skill_id>/', views.delete_skill, name='delete_skill'),
    path('all_data/', views.all_data_view, name='all_data_view'),
   


]
