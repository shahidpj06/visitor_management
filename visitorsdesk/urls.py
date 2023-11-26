from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_page, name='login'),
    path('register/', views.register_page, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('logout/', views.logout_page, name='logout'),
    path('settings/', views.main_settings, name='settings'),
    path('visitors/', views.visitors_page, name='visitors'),
    path('create-branch/', views.create_branch, name='create-branch'),
    path('delete/', views.delete, name='delete'),
    path('user-info/', views.user_info, name='user-info'),
    path('invite-visitor/', views.invite_visitor, name='invite-visitor'),
    path('checkin_visitor/', views.checkin_visitor, name='checkin_visitor'),
    path('add_desk/', views.add_desk, name='add_desk'),
    path('new_visitor/', views.new_visitor, name='new_visitor'),
    path('get_dependent/', views.get_dependent, name='get_dependent'),
    path('exit_visitor/', views.exit_visitor, name='exit_visitor'),
    path('append_checkout_modal/',views.append_checkout_modal,name='append_checkout_modal'),
    path('invited_visitor_check/', views.invited_visitor_check, name='invited_visitor_check'),
]
