import re # Regular Expression
import qrcode
from . models import *
from io import BytesIO
from . serializer import *
from django.views import View
from datetime import datetime
from celery import shared_task
from django.conf import settings
from django.contrib import messages
from datetime import date, timezone
from django.http import JsonResponse
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from django.core.serializers.json import DjangoJSONEncoder
from django.core.paginator import Paginator
from django.template.loader import render_to_string
from django.core.mail import send_mail, EmailMessage
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt
from django import forms
from datetime import timedelta
from django.db.models import Q



def is_strong_password(password):
    if len(password) < 8:
        return False

    if not re.search('[a-zA-Z]', password):
        return False

    if not re.search('[0-9]', password):
        return False

    if not re.search('[!@#$%^&*()-_+={}[]|\:;",<.>/?]', password):
        return False

    return True

def user_profile(request):
    print("request.user::::::::::",request.user.id)
    auth_user = User.objects.get(id=request.user.id)
    user_data = MainUser.objects.get(auth_user=request.user.id)
    context = {
        'user_data': user_data
    }
    return render(request, 'profile.html', context)



def register_page(request):
    if request.method == 'POST': 
        username = request.POST.get('username').strip().lower()
        useremail = request.POST.get('useremail').strip().lower()
        userpassword = request.POST.get('userpassword').strip()

        existing_username = User.objects.filter(username=username).exists()
        existing_email = User.objects.filter(email=useremail).exists()
        weak_password = userpassword != '' and not is_strong_password(userpassword)
         
        if existing_username and existing_email and userpassword and weak_password:
            return JsonResponse({"status": 400, "value": [
                {"status": 400, "type": 'username', "error": "Username already exists. Please use a different one."},
                {"status": 400, "type": "email", "error": "Email address already exists. Please choose a different email."}, 
                {'status': 400, "type": "password", "error": "Weak password: Mix case, symbols, numbers & min 8 characters."}
                ]})
        
        if existing_email and weak_password:
            return JsonResponse({"status": 400, "value": [
                {"status": 400, "type": "email", "error": "Email address already exists. Please choose a different email."}, 
                {'status': 400, "type": "password", "error": "Weak password: Mix case, symbols, numbers & min 8 characters."}
                ]})
        
        if existing_username and weak_password:
            return JsonResponse({"status": 400, "value": [
                {"status": 400, "type": 'username', "error": "Username already exists. Please use a different one."}, 
                {'status': 400, "type": "password", "error": "Weak password: Mix case, symbols, numbers & min 8 characters."}
                ]})
        
        if existing_username and existing_email:
            return JsonResponse({"status": 400, "value": [
                {"status": 400, "type": 'username', "error": "Username already exists. Please use a different one."},
                {"status": 400, "type": "email", "error": "Email address already exists. Please choose a different email."}
                ]})
        
        elif existing_username:
            return JsonResponse({"status": 400, "type": "username", "error": "Username already exists. Please use a different one."})
        
        elif existing_email:
            return JsonResponse({"status": 400, "type": "email", "error": "Email address already exists. Please choose a different email."})
        
        if weak_password:
            return JsonResponse({'status': 400, "type": "password", "error": "Weak password: Mix case, symbols, numbers & min 8 characters."})
      
        my_user = User.objects.create(username=username, email=useremail)
        my_user.set_password(userpassword)
        my_user.save()
        
        company_id = Company.objects.create(user_profile=my_user)
        MainUser.objects.create(auth_user=my_user, username=username, useremail=useremail, company=company_id, user_role="Company Admin")
        login(request, my_user)
        return JsonResponse({"status": 200, "message": "User registered successfully", "icon": "success"})
    
    return render(request, 'register.html')

@login_required(login_url='login')
def edit_company_admin(request, user_id):
    user = get_object_or_404(MainUser, id=user_id)

    if request.method == 'POST':
        user.first_name = request.POST.get('first_name').strip()
        print(user.first_name)
        user.last_name = request.POST.get('last_name').strip()
        user.useremail = request.POST.get('useremail').strip().lower()
        user.user_phone = request.POST.get('user_phone').strip()
        user.username = request.POST.get('username').strip().lower()
        user.user_role = "Company Admin" 
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        current_password = request.POST.get('current_password')

        if password or confirm_password:
            if not current_password or not request.user.check_password(current_password):
                return JsonResponse({"status": 400, "type": "current_password", "error": "Invalid current password."})

            if password != confirm_password:
                return JsonResponse({"status": 400, "type": "confirm_password", "error": "Passwords do not match."})
            form = PasswordChangeForm(request.user, {'new_password1': password, 'new_password2': confirm_password})

            if form.is_valid():
                form.save()
                update_session_auth_hash(request, form.user) 
            else:
                return JsonResponse({"status": 400, "type": "password", "error": form.errors})

        if 'profile_image' in request.FILES:
            user.profile_image = request.FILES['profile_image']
        user.about = request.POST.get('about').strip()

        if MainUser.objects.filter(useremail=user.useremail).exclude(id=user.id).exists():
            return JsonResponse({"status": 400, "type": "user_email", "error": "Email already exists. Please choose a different email."})

        if MainUser.objects.filter(username=user.username).exclude(id=user.id).exists():
            return JsonResponse({"status": 400, "type": "username", "error": "Username already exists. Please use a different one."})

        user.save()
        updated_data = UserSerializer(user).data
        return JsonResponse({"status": 200, 'message': "User updated", 'icon': 'success', 'updated_data': updated_data})

    # user_data = UserSerializer(user).data
    # return JsonResponse({"status": 200, 'user_data': user_data})

@csrf_exempt
def login_page(request):
    if request.method == 'POST':
        username = request.POST.get('username').strip().lower()
        userpassword = request.POST.get('userpassword')

        if not username or not userpassword:
            return JsonResponse({"status": 400, "value": [{"status": 400, "type": "empty", "error": "Both username and password are required."}]})

        user = authenticate(request, username=username, password=userpassword)

        if user is not None:
            login(request, user)
            return JsonResponse({"status":200})
        if not User.objects.filter(username=username).exists() and not authenticate(userpassword=userpassword):
            return JsonResponse({"status": 400, "value":[{"status": 400, "type": "username", "error": "Incorrect Username."},
                                                         {"status": 400, "type": "password", "error": "Incorrect Password"}]})
        elif not User.objects.filter(username=username).exists():
            return JsonResponse({"status": 400, "type": "username", "error": "Incorrect Username."})
        else:
            return JsonResponse({"status": 400, "type": "password", "error": "Incorrect Password."})
            
    return render(request, 'index.html')


@login_required(login_url='login')
def dashboard(request):
    current_date = datetime.today()
    visitor_data = NewVisitor.objects.filter(auth_user=request.user).order_by("id")
    visitor_today_data = NewVisitor.objects.filter(auth_user=request.user, checkin_time__date=current_date).order_by("id")
    checkout_count = ExitVisitor.objects.filter(auth_user=request.user, exit_time__date=current_date).count()
    expected_visitor = InviteVisitor.objects.filter(auth_user=request.user).order_by("id")
    context = { # context - mapping to template.
        'visitor_data': visitor_data,
        'checkout_count': checkout_count,
        'expected_visitor': expected_visitor,
        'visitor_today_data': visitor_today_data
    }
    return render(request, 'dashboard.html', context)


def logout_page(request):
    logout(request)
    return redirect('login')

@login_required(login_url='login')
def main_settings(request):
    data = Branch.objects.filter(auth_user=request.user).order_by("id")
    company_data = Company.objects.get(user_profile=request.user)
    user_data = MainUser.objects.filter(company=company_data.id).exclude(user_role='Company Admin')
    desk_data = Desk.objects.filter(auth_user=request.user)
    context = {
        'data':data,
        'user_data' :user_data,
        'desk_data' :desk_data,
    }

    return render(request, 'settings.html', context)

@login_required(login_url='login')
def visitors_page(request):
    data = Branch.objects.filter(auth_user=request.user)
    user_data = MainUser.objects.filter(auth_user=request.user)
    visitor_data = InviteVisitor.objects.filter(auth_user=request.user)
    checkin_visitor_data = NewVisitor.objects.filter(auth_user=request.user)
    checkout_visitor_data = ExitVisitor.objects.filter(auth_user=request.user)
    context = {
        'data':data,
        'user_data': user_data,
        'visitor_data': visitor_data,
        'checkin_visitor_data': checkin_visitor_data,
        'checkout_visitor_data': checkout_visitor_data,
    }
    return render(request, 'visitors.html', context)


@login_required(login_url='login')
def create_branch(request):
    if request.method == 'POST':
        try:
            users_data = MainUser.objects.filter(auth_user=request.user).first()
        except MainUser.MultipleObjectsReturned:
            users_data = None

        companyid = users_data.company
        name = request.POST.get("name").strip()
        if Branch.objects.filter(name__iexact=name, auth_user=request.user).exists():
            return JsonResponse({"status": 400, "type": "branch_name", "error": "Branch name must be unique"})

        branch_code = request.POST.get("branch_code").strip()
        if Branch.objects.filter(branch_code=branch_code, auth_user=request.user).exists():
            return JsonResponse({"status": 400, "type": "branch_code", "error": "Branch code must be unique"})
        
        if Branch.objects.filter(branch_code=branch_code, auth_user=request.user).exists() and Branch.objects.filter(name=name, auth_user=request.user).exists():
            return JsonResponse({"status": 400, "value": [
                {"status": 400, "type": "branch_code", "error": "Branch code must be Unique"},
                {"status": 400, "type": "branch_name", "error": "Branch name must be Unique"}
            ]})

        country_code = request.POST.get("country_code").strip()
        country_timezone = request.POST.get("country_timezone")
        main_branch = Branch.objects.create(auth_user=request.user, name=name, company=companyid,
                                branch_code=branch_code, country_code=country_code,
                                country_timezone=country_timezone)
        created_branch_data = BranchSerializer(main_branch).data
        branch_data = Branch.objects.filter(auth_user=request.user)
        branch_data_count = branch_data.count()
        return JsonResponse({"status": 200, 'message': "Branch created", 'icon': 'success',
                            'created_branch_data': created_branch_data, 'branch_data_count': branch_data_count})


@login_required(login_url='login')
def edit_branch(request, branch_id):
    branch = get_object_or_404(Branch, id=branch_id, auth_user=request.user)

    if request.method == 'POST':
        branch.name = request.POST.get("name").strip().lower()
        if Branch.objects.filter(name=branch.name, auth_user=request.user).exclude(id=branch.id).exists():
            return JsonResponse({"status": 400, "type": "branch_name", "error": "Branch came must be Unique"})
        
        branch.branch_code = request.POST.get("branch_code").strip()
        if Branch.objects.filter(branch_code=branch.branch_code).exclude(id=branch.id).exists():
            return JsonResponse({"status": 400, "type": "branch_code", "error": "Branch Code must be Unique"})

        branch.country_code = request.POST.get("country_code").strip()
        branch.save()
        updated_branch_data = BranchSerializer(branch).data
        branch_data = Branch.objects.filter(auth_user=request.user)
        branch_data_count = branch_data.count()
        return JsonResponse({"status": 200, 'message': "Branch updated", 'icon': 'success',
                             'updated_branch_data': updated_branch_data, 'branch_data_count': branch_data_count})

    # branch_data = BranchSerializer(branch).data
    # return JsonResponse({"status": 200, 'branch_data': branch_data})

    

def get_branches(request):
    branches = Branch.objects.filter(auth_user=request.user)
    serializer = BranchSerializer(branches, many=True)
    return JsonResponse(serializer.data, safe=False)

def get_branches_user(request):
    branches = Branch.objects.filter(auth_user=request.user)
    serializer = BranchSerializer(branches, many=True)
    return JsonResponse(serializer.data, safe=False)

def get_desk_details(request, desk_id):
    try:
        desk = Desk.objects.get(id=desk_id)
        serializer = DeskSerializer(desk)
        return JsonResponse({'status': 200, 'desk_details': serializer.data})
    except Desk.DoesNotExist:
        return JsonResponse({'status': 404, 'error': 'Desk not found'})


@login_required(login_url='login')
def delete(request):
    if request.method == 'POST':
        delete_id = request.POST.get("delete_id")
        delete_type = request.POST.get("delete_type")
        if delete_type == "user":
            user = MainUser.objects.get(id=delete_id) # for getting single user
            user.delete()
            return JsonResponse({'message': "User deleted successfully", 'icon': 'success'})
        if delete_type == 'branch':
            branch = Branch.objects.get(id=delete_id)
            branch.delete()
            return JsonResponse({'message': "Branch deleted successfully", 'icon': 'success','id': delete_id})
        if delete_type == 'desk':
            desk = Desk.objects.get(id=delete_id)
            desk.delete()
            return JsonResponse({'message': "Desk deleted successfully", 'icon': 'success', 'id': delete_id})
        

@login_required(login_url='login')
def user_info(request):
    if request.method == 'POST':
        user = request.user
        try:
            users_data = MainUser.objects.filter(auth_user=user).first()
        except MainUser.MultipleObjectsReturned:
            users_data = None

        companyid = users_data.company
        first_name = request.POST.get('first_name').strip()
        last_name = request.POST.get('last_name').strip()
        user_email = request.POST.get('user_email').strip().lower()     
        user_phone = request.POST.get('user_phone').strip()
        user_name = request.POST.get('user_name').strip().lower()

        if MainUser.objects.filter(useremail=user_email).exists() and MainUser.objects.filter(username=user_name).exists():
            return JsonResponse({'status': 400, 'value': [{"status": 400, "type": "useremail", "error": "Email already exists. Please choose a different email."},
                                {"status": 400, "type": "username", "error": "Username already exists. Please use a different one."}]})

        elif MainUser.objects.filter(useremail=user_email).exists():
            return JsonResponse({'status': 400, 'type': "useremail", "error": "Email already exists. Please choose a different email." })
        
        elif MainUser.objects.filter(username=user_name).exists():
            return JsonResponse({"status": 400, "type": "username", "error": "Username already exists. Please use a different one."})

        # user_password = request.POST.get('user_password')
        user_role = request.POST.get('user_role')
        branch_id = request.POST.get('branch_id')
        
        if branch_id is None:
            return JsonResponse({'message': "Please select a branch", 'icon': 'error'})
        branch = Branch.objects.filter(pk=branch_id).first()

        auth_user_data = User.objects.create_user(username=user_name, email=user_email)
        auth_user_data.save()
        
        main_user = MainUser.objects.create(auth_user=auth_user_data, first_name=first_name,
                                last_name=last_name, useremail=user_email, company=companyid,
                                user_phone=user_phone, username=user_name,
                                user_role=user_role, primary_branch=branch)
        
        created_data = UserSerializer(main_user).data
        user_data = MainUser.objects.filter(auth_user=request.user)
        user_data_count = user_data.count()
        return JsonResponse({"status": 200, 'message': "Successfully created user", 'icon': 'success', 'form_name': "user_info", "created_data": created_data,
                             'user_data_count': user_data_count})
    

@login_required(login_url='login')
def edit_user(request, user_id):
    user = get_object_or_404(MainUser, id=user_id)

    if request.method == 'POST':
        user.first_name = request.POST.get('first_name').strip()
        user.last_name = request.POST.get('last_name').strip()
        user.useremail = request.POST.get('user_email').strip().lower()
        user.user_phone = request.POST.get('user_phone').strip()
        user.username = request.POST.get('user_name').strip().lower()
        user.user_role = request.POST.get('user_role').strip()
        branch_id = request.POST.get('branch_id')

        if not branch_id:
            return JsonResponse({"status": 400, 'error': 'Please select a branch'})

        branch = get_object_or_404(Branch, id=branch_id)
        user.primary_branch = branch

        if MainUser.objects.filter(useremail=user.useremail).exclude(id=user.id).exists():
            return JsonResponse({"status": 400, "type": "user_email", "error": "Email already exists. Please choose a different email."})

        if MainUser.objects.filter(username=user.username).exclude(id=user.id).exists():
            return JsonResponse({"status": 400, "type": "user_name", "error": "Username already exists. Please use a different one."})

        user.save()
        updated_data = UserSerializer(user).data
        user_data_count = MainUser.objects.filter(auth_user=request.user).count()

        return JsonResponse({"status": 200, 'message': "User updated", 'icon': 'success',
                             'updated_data': updated_data, 'user_data_count': user_data_count})

    user_data = UserSerializer(user).data
    return JsonResponse({"status": 200, 'user_data': user_data})



def get_branch_counter(branch_name):
    try:
        branch = Branch.objects.filter(name=branch_name).first()
        if branch:
            return branch.counter
        else:
            return 1
    except Branch.MultipleObjectsReturned:
        return 1


def update_branch_counter(branch_name, new_counter):
    try:
        branch = Branch.objects.filter(name=branch_name).first()
        # branch = Branch.objects.select_for_update().get(name=branch_name)
        branch.counter = new_counter
        branch.save()
    except Branch.MultipleObjectsReturned:
        pass
        

def generate_visitor_id(companyid, branch_slug, branch_counter):
    branch_code = branch_slug[:2].upper()
    branch_counter += 1
    unique_id = f"{branch_code}{companyid}{str(branch_counter).zfill(4)}"
    update_branch_counter(branch_slug, branch_counter)
    return unique_id


def invitation_email(visitor_email, full_name, branch, main_user, visitor_id, purpose, from_date, to_date, qr_code_image):
    message = render_to_string('invitation_email.html', {
        'full_name': full_name,
        'branch': branch,
        'main_user': main_user,
        'purpose': purpose,
        'visitor_id': visitor_id,
        'from_date': from_date,
        'to_date': to_date,
    })

    subject = "Invitation to Visit"
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [visitor_email]
    email = EmailMessage(subject, message, from_email, recipient_list)
    email.content_subtype = "html"
    email.attach("qr_code.png", qr_code_image, "image/png")
    email.send()


def get_dependent(request):
    branch_id = request.GET.get('branch_id')
    if branch_id:
        branch = Branch.objects.get(pk=branch_id)
        hosts = MainUser.objects.filter(primary_branch=branch)
        host_data = [{'id': host.id, 'name': f"{host.first_name} {host.last_name}"} for host in hosts]

        desks = Desk.objects.filter(select_branch=branch)
        desk_data = [{'id': desk.id, 'name': desk.desk_name} for desk in desks]
        return JsonResponse({'hosts': host_data,'desks': desk_data})
    else:
        return JsonResponse({'hosts': []}, {'desks': []})
    # 

@login_required(login_url='login')
def invite_visitor(request):
    if request.method == 'POST':
        try:
            users_data = MainUser.objects.filter(auth_user=request.user).first()
        except MainUser.MultipleObjectsReturned:
            users_data = None

        if users_data and users_data.company:
            companyid = users_data.company.id
        else:
            companyid = None              
        full_name = request.POST.get('full_name').strip()
        
        if full_name is None:
            return JsonResponse({"status": 400, "type": "full_name", "error": "full name"})
        
        visitor_email = request.POST.get('visitor_email').strip()
        from_date = request.POST.get('from_date')
        to_date = request.POST.get('to_date')
        current_date = datetime.now().isoformat()
        visitor_phone = request.POST.get('visitor_phone').strip()
        purpose = request.POST.get('purpose').strip()
        branch_id = request.POST.get('branch_id')
        
        if branch_id is None:
            return JsonResponse({"status": 400, "type": "branchid", "error": "Select branch"})
        branch = Branch.objects.filter(pk=branch_id).first()
        user_id = request.POST.get('user_id')

        if not user_id:
            return JsonResponse({"status": 400, "type": "userid", "error": "Select Host"})
       
        main_user = MainUser.objects.filter(pk=user_id).first()
        visitor_id = generate_visitor_id(companyid, branch.name, branch.counter)

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )

        qr.add_data(visitor_id)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        img_buffer = BytesIO()
        img.save(img_buffer, "png")
        img_buffer.seek(0)

        invitation_email(
                visitor_email, full_name, branch.name, f"{main_user.first_name} {main_user.last_name}", visitor_id, purpose, from_date, to_date, img_buffer.read()
            )
        
        invite_visitor = InviteVisitor.objects.create(purpose=purpose, company_id=companyid, auth_user=request.user, full_name=full_name, visitor_email=visitor_email,
            from_date=from_date, to_date=to_date, visitor_phone=visitor_phone, select_branch=branch, user_host=main_user, visitor_id=visitor_id)
        
        created_visitor_data = InviteVisitorSerializer(invite_visitor).data
        visitor_id = created_visitor_data['visitor_id']
        invite_visitor_data = InviteVisitor.objects.filter(auth_user=request.user)
        invite_visitor_data_count = invite_visitor_data.count()
        return JsonResponse({"status": 200, 'message': "Invited", 'icon': "success", 'form_name': 'invite_visitor',
                            'created_visitor_data': created_visitor_data, 'invite_visitor_data_count': invite_visitor_data_count, 'visitor_id': visitor_id})
    

@shared_task
def send_email_async(subject, message, from_email, recipient_list):
    send_mail(subject, message, from_email, recipient_list)


@login_required(login_url='login')
def add_desk(request):
    if request.method == 'POST':
        try:
            users_data = MainUser.objects.filter(auth_user=request.user).first()
        except MainUser.MultipleObjectsReturned:
            users_data = None

        companyid = users_data.company
        desk_name = request.POST.get('desk_name').strip()
        branch_id = request.POST.get('branch_id')

        if branch_id is None:
            return JsonResponse({"status": 400, "type": "desk_branchid", 'message': "Select Branch", 'icon': 'error'})
        branch = Branch.objects.filter(pk=branch_id).first()
        main_desk = Desk.objects.create(auth_user=request.user, company=companyid, desk_name=desk_name, select_branch=branch)
        
        created_desk_data = DeskSerializer(main_desk).data
        desk_data = Desk.objects.filter(auth_user=request.user)
        desk_data_count = desk_data.count()
        return JsonResponse({"status": 200, 'message': "Desk Created", 'icon': 'success', 'created_desk_data': created_desk_data, 'desk_data_count': desk_data_count})
 
    
@login_required(login_url='login')
def edit_desk(request, desk_id):
    desk = get_object_or_404(Desk, id=desk_id, auth_user=request.user)

    if request.method == 'POST':
        desk_name = request.POST.get('desk_name').strip()
        branch_id = request.POST.get('branch_id')

        if branch_id is None:
            return JsonResponse({"status": 400, "type": "desk_branchid", 'message': "Select Branch", 'icon': 'error'})

        branch = Branch.objects.filter(pk=branch_id).first()
        desk.desk_name = desk_name
        desk.select_branch = branch
        desk.save()

        updated_desk_data = DeskSerializer(desk).data
        desk_data = Desk.objects.filter(auth_user=request.user)
        desk_data_count = desk_data.count()
        
        return JsonResponse({"status": 200, 'message': "Desk updated", 'icon': 'success',
                             'updated_desk_data': updated_desk_data, 'desk_data_count': desk_data_count})

    desk_data = DeskSerializer(desk).data
    return JsonResponse({"status": 200, 'desk_data': desk_data})

# 
def checkin_visitor(request):
    branch_data = Branch.objects.filter(auth_user=request.user)
    visitor_data = NewVisitor.objects.filter(auth_user=request.user)
    invited_visitor_data = InviteVisitor.objects.filter(auth_user=request.user)
    desk_data = Desk.objects.filter(auth_user=request.user)
    host_data = MainUser.objects.filter(auth_user=request.user)
    context = {
        'visitor_data': visitor_data,
        'branch_data': branch_data,
        'desk_data': desk_data,
        'host_data': host_data,
        'invited_visitor_data': invited_visitor_data,
    }
    return render(request, 'checkin.html', context)

def get_visitor_details(request, visitor_id):
    try:
        visitor = InviteVisitor.objects.get(visitor_id=visitor_id)
        data = {
            'visitor_id': visitor.visitor_id,
            'full_name': visitor.full_name,
            'select_branch': visitor.select_branch.name,
            'purpose': visitor.purpose,
            'user_host': f"{visitor.user_host.first_name} {visitor.user_host.last_name}",
        }
        return JsonResponse(data)
    except InviteVisitor.DoesNotExist:
        return JsonResponse({'error': 'Visitor not found'}, status=404)
        
# 
def check_in_visitor(request, visitor_id):
    try:
        visitor = InviteVisitor.objects.get(visitor_id=visitor_id)
        if visitor.checked_in:
            return JsonResponse({'status': 200, 'message': 'This visitor has already been checked in', 'icon': "error"})
        
        desk_id = request.POST.get('desk_name')
        desk = get_object_or_404(Desk, id=desk_id)
        visitor.checked_in = True
        visitor.save()

        NewVisitor.objects.create(
            full_name=visitor.full_name,
            email=visitor.visitor_email,
            phone=visitor.visitor_phone,
            purpose=visitor.purpose,
            visitor_id=visitor.visitor_id,
            auth_user=visitor.auth_user,
            user_host=visitor.user_host,
            select_branch=visitor.select_branch,
            select_desk=desk,
        )

        return JsonResponse({'message': 'Checked in successfully'})
    except InviteVisitor.DoesNotExist:
        return JsonResponse({'error': 'Visitor not found'}, status=404)


def get_checkin_data(request):
    checkin_data = InviteVisitor.objects.filter(checkin_time__isnull=False)
    serialized_data = InviteVisitorSerializer(checkin_data, many=True).data
    return render(request, 'checkin_data.html', {'checkin_data': serialized_data})


@login_required(login_url='login')
def new_visitor(request):
    if request.method == 'POST':
        try:
            users_data = MainUser.objects.filter(auth_user=request.user).first()
        except MainUser.MultipleObjectsReturned:
            users_data = None

        if users_data and users_data.company:
            companyid = users_data.company.id
        else:
            companyid = None      

        full_name = request.POST.get('full_name').strip()
        email = request.POST.get('email').strip()
        phone = request.POST.get('phone').strip()
        purpose = request.POST.get('purpose').strip()
        branch_id = request.POST.get('branch_id')
        checkin_time = datetime.now()
        print(checkin_time)

        if not branch_id:
            return JsonResponse({'status': 400, 'type': 'branchId', 'error': 'Select a branch'})
        branch = Branch.objects.filter(pk=branch_id).first()
        desk_id = request.POST.get('desk_id')

        if not desk_id:
            return JsonResponse({'status': 400, 'type': 'deskId', 'error': 'Choose the desk'})            
        desk = Desk.objects.filter(pk=desk_id).first()
        host_id = request.POST.get('host_id')
        
        if not host_id:
            return JsonResponse({'status': 400, 'type': 'hostId', 'error': 'Choose a host'})
        host = MainUser.objects.filter(pk=host_id).first() 
        visitor_id = generate_visitor_id(companyid, branch.name, branch.counter)

        NewVisitor.objects.create(auth_user=request.user, full_name=full_name, email=email, phone=phone, company_id=companyid,
                                  purpose=purpose, select_branch=branch, user_host=host,
                                  select_desk=desk, visitor_id=visitor_id)
        return JsonResponse({"status": 200, 'message': 'Added Successfully', 'icon': 'success', 'checkin_time': checkin_time})
    

    
@login_required(login_url='login')
def exit_visitor(request):
    if request.method == 'POST':
        try:
            users_data = MainUser.objects.filter(auth_user=request.user).first()
        except MainUser.MultipleObjectsReturned:
            users_data = None

        companyid = users_data.company
        exit_desk = request.POST.get('exit_desk')

        if not exit_desk:
            return JsonResponse({'status': 400, 'message': 'Desk is required', 'icon': 'error'})
        visitor_id = request.POST.get('visitor_id')
        
        try:
            visitor = NewVisitor.objects.filter(visitor_id=visitor_id, auth_user=request.user).first()
        except NewVisitor.DoesNotExist:
            return JsonResponse({'status': 400, 'type': 'notexist', 'error': 'Visitor not found'})
        
        if visitor.checkout_time is not None:
            return JsonResponse({'status': 400, 'type': 'checkouttime', 'message': 'Oops! It seems this visitor has already checked out.', 'icon': 'error'})
        
        exit_time = datetime.now()
        visitor_remarks = request.POST.get('visitor_remarks')

        current_date = datetime.now().isoformat()
        
        visitor.checkout_time = exit_time  
        visitor.save()


        ExitVisitor.objects.create(auth_user=request.user, exit_desk_id=exit_desk,
                                   exit_time=exit_time, company=companyid,
                                     visitor_remarks=visitor_remarks)
        
        return JsonResponse({ "status": 200, 'message': 'Visitor Checked out successfully', 'icon': 'success', 'current_date': current_date})
                            #  'checkout_time': exit_time.strftime('%Y-%m-%d %H:%M:%S'),
                               


@login_required(login_url='login')
def append_checkout_modal(request):
    visitor_id = request.GET.get("id")
    vid = request.GET.get("vid")
    data = NewVisitor.objects.get(id=visitor_id)
    return render(request,'append_checkout_modal.html', {'data':data,'vid':vid})


@login_required(login_url='login')
def create_event(request):
    if request.method == "POST":
        try:
            users_data = MainUser.objects.filter(auth_user=request.user).first()
        except MainUser.MultipleObjectsReturned:
            users_data = None
        companyid = users_data.company
        visitor_name = request.POST.get('visitor_name')
        visitor_email = request.POST.get('visitor_email')
        event_name = request.POST.get('event_name')
        visitor_phone = request.POST.get('visitor_phone')
        starts_at = request.POST.get('starts_at')
        print(starts_at)
        ends_at = request.POST.get('ends_at')
        print(ends_at)
        host_id = request.POST.get('host_id')
        host = MainUser.objects.filter(pk=host_id).first() 
        event_description = request.POST.get('event_description')

        if Event.objects.filter(Q(auth_user=request.user) & Q(visitor_email=visitor_email)).exists():
            return JsonResponse({"status": 400, "message": "This visitor already booked a slot.", "icon": "success"})
        
        existing_events = Event.objects.filter(
            Q(auth_user=request.user) & Q(starts_at__date=starts_at.date()) & 
            (
                (Q(starts_at__lt=starts_at, ends_at__gt=starts_at)) |
                (Q(starts_at__lt=ends_at, ends_at__gt=ends_at))
            )
        ) 

        if existing_events.exists():
            return JsonResponse()

        Event.objects.create(
            auth_user=request.user,
            company=companyid,
            visitor_name=visitor_name,
            visitor_email=visitor_email,
            visitor_phone=visitor_phone,
            event_name=event_name,
            starts_at=starts_at,
            ends_at=ends_at,
            event_description=event_description,
            staff=host
        )
        
        
        return JsonResponse({"status": 200, "message": "Successfully booked a slot", "icon": "success"})

    return JsonResponse({'error': 'Invalid request'})

@csrf_exempt
def get_events(request):
    try:
        users_data = MainUser.objects.filter(auth_user=request.user).first()
    except MainUser.MultipleObjectsReturned:
        users_data = None

    companyid = users_data.company
    events = Event.objects.filter(company=companyid)

    event_list = []
    for event in events:
        if event.starts_at: 
            starts_at = event.starts_at + timedelta(hours=5, minutes=30)
            event.ends_at = event.ends_at - timedelta(hours=5, minutes=30)
            event.ends_at = event.ends_at + timedelta(days=1)

            event_list.append({
                'visitor_name': event.visitor_name,
                'title': event.event_name,
                'start': starts_at.strftime('%Y-%m-%dT%H:%M:%S%z'),
                'end': event.ends_at.strftime('%Y-%m-%dT%H:%M:%S%z'),
                'description': event.event_description,
            })

    return JsonResponse(event_list, safe=False)



def get_event_details(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    event_details = {
        'visitor_name': event.visitor_name,
        'visitor_email': event.visitor_email,
        'visitor_phone': event.visitor_phone,
        'event_name': event.event_name,
        'starts_at': event.starts_at.isoformat(),
        'ends_at': event.ends_at.isoformat(),
        'host_id': event.staff.id,
        'event_description': event.event_description,
    }

    print("erferferf")
    return JsonResponse(event_details)

@login_required(login_url='login')
def calendar(request):
    checkins = NewVisitor.objects.filter(auth_user=request.user)
    checkouts = ExitVisitor.objects.filter(auth_user=request.user)
    event = Event.objects.filter(auth_user=request.user)
    company_data = Company.objects.get(user_profile=request.user)
    staff_data = MainUser.objects.filter(company=company_data.id).exclude(user_role='Company Admin')

    context = {
        'checkins': checkins,
        'checkouts': checkouts,
        'event': event,
        'staff_data': staff_data,
    }
    return render(request, 'calendar.html', context)

