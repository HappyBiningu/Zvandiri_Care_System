from django.urls import path
from . import views
from .views import chatbot_view

urlpatterns = [
    path('', views.login_view, name='login'),  # Redirect to login if no specific page is requested
    path('dashboard/', views.dashboard, name='dashboard'),  # Dashboard as a protected view
    path('login/', views.login_view, name='login'),  # URL for login page
    path('signup/', views.signup_view, name='signup'),  # URL for signup page
    path('logout/', views.logout_view, name='logout'),  # URL for logout
    path('dashboard/index/', views.home, name='home'),  # Route for index page
    path('dashboard/index/result/', views.result, name='result'),  # Ensure result page is correctly routed
    path('chatbot/', chatbot_view, name='chatbot'),
    path('edit_patient/<int:patient_id>/', views.edit_patient, name='edit_patient'),
    path('delete_patient/<int:patient_id>/', views.delete_patient, name='delete_patient'),

]
