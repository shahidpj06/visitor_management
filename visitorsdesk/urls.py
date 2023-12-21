from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_page, name='login'),
    path('delete/', views.delete, name='delete'),
    path('logout/', views.logout_page, name='logout'),
    path('add_desk/', views.add_desk, name='add_desk'),
    path('calendar/', views.calendar, name='calendar'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('user-info/', views.user_info, name='user-info'),
    path('settings/', views.main_settings, name='settings'),
    path('visitors/', views.visitors_page, name='visitors'),
    path('register/', views.register_page, name='register'),
    path('new_visitor/', views.new_visitor, name='new_visitor'),
    path('create_event/', views.create_event, name='create_event'),
    path('exit_visitor/', views.exit_visitor, name='exit_visitor'),
    path('get-branches/', views.get_branches, name='get_branches'),
    path('user_profile/', views.user_profile, name='user_profile'),
    path('get_events/', views.get_events, name='get_events'),
    path('get_dependent/', views.get_dependent, name='get_dependent'),
    path('create-branch/', views.create_branch, name='create-branch'),
    path('edit_desk/<int:desk_id>/', views.edit_desk, name='edit_desk'),
    path('edit_user/<int:user_id>/', views.edit_user, name='edit_user'),
    path('invite-visitor/', views.invite_visitor, name='invite-visitor'),
    path('checkin_visitor/', views.checkin_visitor, name='checkin_visitor'),
    path('get-checkin-data/', views.get_checkin_data, name='get-checkin-data'),
    path('edit_branch/<int:branch_id>/', views.edit_branch, name='edit_branch'),
    # path('get_calendar_data/', views.get_calendar_data, name='get_calendar_data'),
    path('get-branches-user/', views.get_branches_user, name='get_branches-user'),
    path('append_checkout_modal/',views.append_checkout_modal,name='append_checkout_modal'),
    path('check-in-visitor/<str:visitor_id>/', views.check_in_visitor, name='check_in_visitor'),
    path('edit_company_admin/<int:user_id>/', views.edit_company_admin, name='edit_company_admin'),    
    path('get-visitor-details/<str:visitor_id>/', views.get_visitor_details, name='get_visitor_details'),
    ]
