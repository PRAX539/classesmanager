from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.loginpage,name = "loginpage"),
    path('whats_next', views.whats_next,name = "whats_next"),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('logout',views.logoutpage,name = "logoutpage"),
    path('registeruser',views.registeruser,name = "registeruser"),
    path('dashboard',views.dashboard,name = "dashboard"),
    path('professor_profile',views.professor_profile,name = "professor_profile"),
    path('classes_list', views.classes_list, name = "classes_list"),
    path('add_classes', views.add_classes, name = "add_classes"),
    path('edit_classes/<int:id>', views.edit_classes, name = "edit_classes"),
    path('delete_classes/<int:id>', views.delete_classes, name = "delete_classes"),
    path('standard_list', views.standard_list, name = "standard_list"),
    path('add_standard', views.add_standard, name = "add_standard"),
    path('edit_standard/<int:id>', views.edit_standard, name = "edit_standard"),
    path('delete_standard/<int:id>', views.delete_standard, name = "delete_standard"),
    path('subject_list', views.subject_list, name = "subject_list"),
    path('add_subject', views.add_subject, name = "add_subject"),
    path('edit_subject/<int:id>', views.edit_subject, name = "edit_subject"),
    path('delete_subject/<int:id>', views.delete_subject, name = "delete_subject"),
    path('add_schedule', views.add_schedule, name = "add_schedule"),
    path('edit_schedule/<int:id>', views.edit_schedule, name = "edit_schedule"),
    path('delete_schedule/<int:id>', views.delete_schedule, name = "delete_schedule"),
    path('schedule_list', views.schedule_list, name = "schedule_list"),
    path('reports', views.reports, name = "reports"),
    path('forgot_password', views.forgot_password, name = "forgot_password"),
    path('password_reset_confirm/<uidb64>/<token>/', views.password_reset_confirm, name = "password_reset_confirm"),
    path('change_password/<int:user>', views.change_password, name = "change_password"),
    path('classeswise_income', views.classeswise_income, name = "classeswise_income"),
    path('standardwise_income',views.standardwise_income, name = "standardwise_income"),
    path('subjectwise_income',views.subjectwise_income, name = "subjectwise_income"),
    path('datewise_income',views.datewise_income, name = "datewise_income"),
    # path('mutliparameter_income',views.mutliparameter_income, name = "mutliparameter_income"),
    
]

if settings.DEBUG:
    urlpatterns = urlpatterns + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)