from django.contrib import admin
from . models import *

# Register your models here.
admin.site.register(Branch)

admin.site.register(Event)

@admin.register(MainUser)
class MainUserAdmin(admin.ModelAdmin):
    list_display = [
        'first_name', 'last_name', 'useremail', 'username',
        'user_role', 'primary_branch'
        ]


admin.site.register(Company)

@admin.register(InviteVisitor)
class InviteVisitorAdmin(admin.ModelAdmin):
    list_display = [
        'full_name', 'visitor_email', 'from_date',
        'to_date', 'visitor_phone', 'auth_user',
        'user_host', 'select_branch']
    

@admin.register(Desk)
class DeskAdmin(admin.ModelAdmin):
    list_display = [
        'desk_name', 'select_branch'
    ]

@admin.register(NewVisitor)
class NewVisitorAdmin(admin.ModelAdmin):
    list_display = [
        'full_name', 'email', 'phone', 'purpose'
        
    ]