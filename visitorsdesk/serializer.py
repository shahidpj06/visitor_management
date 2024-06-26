from .models import *
from rest_framework import serializers

class UserSerializer(serializers.ModelSerializer):
    auth_user = serializers.SerializerMethodField()
    primary_branch = serializers.SerializerMethodField()

    class Meta:
        model = MainUser
        fields = '__all__'

    def get_auth_user(self, obj):
        return obj.auth_user.username
    
    def get_primary_branch(self, obj):
        return obj.primary_branch.name
    

class BranchSerializer(serializers.ModelSerializer):
    auth_user = serializers.SerializerMethodField()

    class Meta:
        model = Branch
        fields = '__all__'

    def get_auth_user(self, obj):
        return obj.auth_user.username    
    

class DeskSerializer(serializers.ModelSerializer):
    auth_user = serializers.SerializerMethodField()
    select_branch = serializers.SerializerMethodField()

    class Meta:
        model = Desk
        fields = '__all__'

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
        fields = '__all__'
        
    def get_auth_user(self, obj):
        return obj.auth_user.username
    
    def get_select_branch(self, obj):
        return obj.select_branch.name

    def get_user_host(self, obj):
        return f"{obj.user_host.first_name} {obj.user_host.last_name}"
