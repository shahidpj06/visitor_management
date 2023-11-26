from .models import *
from rest_framework import serializers

class UserSerializer(serializers.ModelSerializer):
    auth_user = serializers.SerializerMethodField()
    primary_branch = serializers.SerializerMethodField()

    class Meta:
        model = MainUser
        fields = ['id', 'first_name', 'last_name', 'user_name', 'user_role', 'primary_branch','auth_user']

    def get_auth_user(self, obj):
        return obj.auth_user.username
    
    def get_primary_branch(self, obj):
        return obj.primary_branch.name
    

class BranchSerializer(serializers.ModelSerializer):
    auth_user = serializers.SerializerMethodField()

    class Meta:
        model = Branches
        fields = ['id', 'name', 'branch_code', 'counter', 'country_code', 'timezone', 'auth_user']

    def get_auth_user(self, obj):
        return obj.auth_user.username    
    

class DeskSerializer(serializers.ModelSerializer):
    auth_user = serializers.SerializerMethodField()
    select_branch = serializers.SerializerMethodField()

    class Meta:
        model = Desk
        fields = ['id', 'desk_name', 'select_branch', 'auth_user']

    def get_auth_user(self, obj):
        return obj.auth_user.username    
    
    def get_select_branch(self, obj):
        return obj.select_branch.name


class InviteVisitorSerializer(serializers.ModelSerializer):
    auth_user = serializers.SerializerMethodField()
    select_branch = serializers.SerializerMethodField()
    user_host = serializers.SerializerMethodField()


    class Meta:
        model = InviteVisitor
        fields = ['id', 'full_name', 'visitor_email', 'visitor_phone', 
                  'purpose', 'visitor_id', 'auth_user', 'user_host',
                  'select_branch']
        
    def get_auth_user(self, obj):
        return obj.auth_user.username
    
    def get_select_branch(self, obj):
        return obj.select_branch.name

    def get_user_host(self, obj):
        return obj.user_host.first_name
