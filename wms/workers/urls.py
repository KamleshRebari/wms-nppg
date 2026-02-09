from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('add/', views.add_worker, name='add_worker'),
    path('display/', views.display, name='display'),

    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('profile/', views.profile_view, name='profile'),
    path('download/', views.download_attendance, name='download_attendance'),
path('dashboard/', views.user_dashboard, name='user_dashboard'),
path("add-worker/", views.add_worker, name="add_worker"),
path("edit-worker/<int:worker_id>/", views.edit_worker, name="edit_worker"),
path("manage-slots/", views.manage_slots, name="manage_slots"),

]

