from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login', views.login, name='login'),
        path('detect_fruit', views.detect_fruit, name='detect_fruit'),
    path('uploaded_file/<str:filename>/', views.uploaded_file, name='uploaded_file'),

    path('adminn',views.admin_rg,name = 'adminn'),
    path('delete_admin', views.delete_admin, name='delete_admin'),
    path('edit_admin', views.edit_admin, name='edit_admin'),
    path('admin_rg',views.admin_rg, name='admin_rg'),
    path('bnb', views.bnb, name='bnb'),
    path('del_admin/<id>', views.del_admin, name='del_admin'),
    path('edit_admin',views.edit_admin, name='edit_admin'),
    path('logged_out', views.logged_out, name='logged_out'),
    path('login',views.login,name = 'login'),
    path('logout', views.logout, name='logout'),
    path('admin_home',views.admin_home, name='admin_home'),
    path('adminn_details', views.adminn_details, name='adminn_details'),
            path('register_employee',views.register_employee, name='register_employee'),
    path('employee_home',views.employee_home, name='employee_home'),
     path('del_employee/<int:id>/', views.del_employee, name='del_employee'),
      path('update_employee',views.update_employee,name = 'update_employee'),
           path('del_new_user/<int:id>/', views.del_new_user, name='del_new_user'),
                   path('feedback', views.feedback, name='feedback'),  
        path('v_feedback', views.v_feedback, name='v_feedback'),  
        path('upload_images',views.upload_images,name='upload_images'),
        path('upload_images/<int:upload_id>/delete/', views.delete_uploads, name='delete_uploads'),
        path('view',views.view, name='view'),
    path('feedback/<int:feedback_id>/delete/', views.delete_feedback, name='delete_feedback'),
    path('mailing', views.mailing, name='mailing'), 
path('forgot_password', views.forgot_password, name='forgot_password'),
]