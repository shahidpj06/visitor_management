from django.db import models
from django.contrib.auth.models import User


class Branches(models.Model):
    auth_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=25, blank=False)
    branch_code = models.CharField(max_length=4, help_text="4 uppercase letters or numbers", blank=False)
    counter = models.PositiveIntegerField(default=1) # for id
    country_code = models.CharField(max_length=25)
    timezone = models.CharField(max_length=50)

    class Meta:
        unique_together = ('auth_user', 'branch_code')

    def __str__(self):
        return self.name
    

class MainUser(models.Model):
    USER_ROLE_MANAGER = 'Manager'
    USER_ROLE_STAFF = 'Staff'
    USER_ROLE_HOST = 'Host'
    USER_ROLE_CHOICES = [
        (USER_ROLE_MANAGER, 'Manager'),
        (USER_ROLE_STAFF, 'Staff'),
        (USER_ROLE_HOST, 'Host'), 
    ]
    auth_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    first_name = models.CharField(max_length=25)
    last_name = models.CharField(max_length=25)
    user_email = models.EmailField(unique=True)
    user_phone = models.CharField(max_length=25)
    user_name = models.CharField(unique=True, max_length=25)
    user_role = models.CharField(max_length=25, choices=USER_ROLE_CHOICES)
    primary_branch = models.ForeignKey(Branches, on_delete=models.CASCADE, related_name='user_profiles')

    def __str__(self): # magic method
        return f"{self.first_name} {self.last_name}"
    

class InviteVisitor(models.Model):
    full_name = models.CharField(max_length=25)
    visitor_email = models.EmailField()
    from_date = models.DateTimeField()
    to_date = models.DateTimeField()
    visitor_phone = models.CharField(max_length=25)
    visitor_id = models.CharField(max_length=8)
    purpose = models.CharField(max_length=25)
    auth_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    user_host = models.ForeignKey(MainUser, on_delete=models.CASCADE, related_name='hosted_user')
    select_branch = models.ForeignKey(Branches, on_delete=models.CASCADE, related_name='invited_vistor')
    

    def __str__(self):
        return self.full_name
    
    class Meta:
        unique_together = ('visitor_id', 'select_branch')
    

class Desk(models.Model):
    desk_name = models.CharField(max_length=25)
    auth_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    select_branch = models.ForeignKey(Branches, on_delete=models.CASCADE, related_name='add_desk')

    def __str__(self):
        return self.desk_name


class NewVisitor(models.Model):
    full_name = models.CharField(max_length=25)
    email = models.EmailField()
    phone = models.CharField(max_length=25)
    purpose = models.CharField(max_length=25)
    visitor_id = models.CharField(max_length=6,null=True,blank=True)
    auth_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    user_host = models.ForeignKey(MainUser, on_delete=models.CASCADE, related_name='host_new_visitor')
    select_branch = models.ForeignKey(Branches, on_delete=models.CASCADE, related_name='branch_new_visitor')
    select_desk = models.ForeignKey(Desk, on_delete=models.CASCADE, related_name='desk_new_visitor')
    checkout_time = models.DateTimeField(null=True, blank=True)
    checkin_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.full_name
    
    
class ExitVisitor(models.Model):
    exit_time = models.DateTimeField()
    visitor_remarks = models.TextField()
    visitor_id = models.CharField(max_length=25, null=True, blank=True)
    auth_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    exit_desk = models.ForeignKey(Desk, on_delete=models.CASCADE, related_name='exit_desk')

    def __str__(self):
        return self.auth_user.username

    
class CheckExistVisitor(models.Model):
    full_name = models.CharField(max_length=25)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=25)
    purpose = models.CharField(max_length=25)
    auth_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    user_host = models.ForeignKey(MainUser, on_delete=models.CASCADE, related_name='host_exist_visitor')
    select_branch = models.ForeignKey(Branches, on_delete=models.CASCADE, related_name='branch_exist_visitor')
    select_desk = models.ForeignKey(Desk, on_delete=models.CASCADE, related_name='desk_exist_visitor')
    checkout_time = models.DateTimeField(null=True, blank=True)
    checkin_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.full_name