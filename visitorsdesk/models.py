from django.db import models
from django.contrib.auth.models import User


class Company(models.Model):
    name = models.CharField(max_length=255, null=True)
    user_profile = models.ForeignKey(User, on_delete=models.CASCADE, null=True)


class Branch(models.Model):
    name = models.CharField(max_length=25, null=True)
    slug = models.SlugField(unique=True, null=True, blank=True)
    branch_code = models.CharField(max_length=4, blank=False, null=True)
    counter = models.PositiveIntegerField(default=1, null=True) # for id
    country_code = models.CharField(max_length=25, null=True)
    country_timezone = models.CharField(max_length=50)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True)
    auth_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='branches')

    class Meta: # change the behavior of the model 
        unique_together = ('auth_user', 'name', 'branch_code')

    def __str__(self):
        return self.name


class MainUser(models.Model):   
    USER_ROLE_CHOICES = (
        ('Company Admin', 'Company Admin'),
        ('Manager', 'Manager'),
        ('Staff', 'Staff'),
        ('Host', 'Host'),
    )
    first_name = models.CharField(max_length=25, null=True)
    last_name = models.CharField(max_length=25, null=True)
    useremail = models.EmailField(max_length=25)
    user_phone = models.CharField(max_length=25, null=True)
    username = models.CharField(max_length=25)
    user_role = models.CharField(max_length=25, choices=USER_ROLE_CHOICES)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True)
    auth_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    primary_branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='user_profiles', null=True)
    profile_image = models.ImageField(upload_to='profile_images/', null=True, blank=True)
    about = models.TextField(null=True, blank=True)

    def __str__(self): # magic method
        return f"{self.first_name} {self.last_name}"
    
    class Meta:
        unique_together = ('auth_user', 'useremail', 'username')
    

class InviteVisitor(models.Model):
    VISITOR_STATUS = {
        ('Invited Visitor', 'Invited Visitor'),
        ('Booked Visitor', 'Booked Visitor')
    }
    full_name = models.CharField(max_length=25, null=True)
    visitor_email = models.EmailField(null=True)
    from_date = models.DateTimeField(null=True)
    to_date = models.DateTimeField(null=True)
    visitor_phone = models.CharField(max_length=25, null=True)
    visitor_id = models.CharField(max_length=8, unique=True)
    purpose = models.CharField(max_length=25)
    visitors_status = models.CharField(max_length=25, choices=VISITOR_STATUS)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True)
    auth_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    user_host = models.ForeignKey(MainUser, on_delete=models.CASCADE, related_name='hosted_user')
    select_branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='invited_vistor', null=True)
    checked_in = models.BooleanField(default=False, null=True)
    checked_out_at = models.DateTimeField(blank=True, null=True)
    event_description = models.TextField(blank=True, null=True)
    

    def __str__(self):
        return self.full_name
    
    class Meta:
        unique_together = ('visitor_id', 'select_branch')
    

class Desk(models.Model):
    desk_name = models.CharField(max_length=25)
    auth_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True)
    select_branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='add_desk')

    def __str__(self):
        return self.desk_name


class NewVisitor(models.Model):
    full_name = models.CharField(max_length=25)
    email = models.EmailField()
    phone = models.CharField(max_length=25)
    purpose = models.CharField(max_length=25)
    visitor_id = models.CharField(max_length=6,null=True,blank=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True)
    auth_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    user_host = models.ForeignKey(MainUser, on_delete=models.CASCADE, related_name='host_new_visitor')
    select_branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='branch_new_visitor')
    select_desk = models.ForeignKey(Desk, on_delete=models.CASCADE, related_name='desk_new_visitor')
    checkout_time = models.DateTimeField(null=True, blank=True)
    checkin_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.full_name
    
    # 
    
class ExitVisitor(models.Model):
    exit_time = models.DateTimeField()
    visitor_remarks = models.TextField()
    visitor_id = models.CharField(max_length=25, null=True, blank=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True)
    auth_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    exit_desk = models.ForeignKey(Desk, on_delete=models.CASCADE, related_name='exit_desk')

    def __str__(self):
        return self.auth_user.username
    
class Event(models.Model):
    visitor_name = models.CharField(max_length=25, null=True)
    visitor_email = models.EmailField(max_length=25, null=True)
    visitor_phone = models.CharField(max_length=25, null=True)
    event_name = models.CharField(max_length=25, null=True)
    starts_at = models.DateTimeField(null=True)
    ends_at = models.DateTimeField(null=True)
    event_description = models.TextField(null=True)
    auth_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    staff = models.ForeignKey(MainUser, on_delete=models.CASCADE, related_name='event_host', null=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.visitor_name

