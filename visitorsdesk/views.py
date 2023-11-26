from datetime import timezone
from datetime import datetime
from django.utils import timezone
import qrcode
from . models import *
from io import BytesIO
from celery import shared_task
from django.conf import settings
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.core.mail import send_mail, EmailMessage
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from . serializer import *


def register_page(request):
    if request.method == 'POST':
        username = request.POST.get('username').strip() 
        useremail = request.POST.get('useremail').strip()
        userpassword = request.POST.get('userpassword').strip()
        # creating user details by POST(create) method. strip() is used for preventing from the whitespace.
         
        if User.objects.filter(username=username).exists() and User.objects.filter(email=useremail).exists(): # checking username and password was exist in the database by filtering() and using exist() keyword.
            return JsonResponse({"status": 400, "value": [{"status": 400, "type": 'username', "error": "Username already exists. Please use a different one."},
                                 {"status": 400, "type": "email", "error": "Email address already exists. Please choose a different email."}]})
        elif User.objects.filter(username=username).exists():
            return JsonResponse({"status":400, "type":"username","error": "Username already exists. Please use a different one."})
        elif User.objects.filter(email=useremail).exists():
            return JsonResponse({"status": 400, "type": "email", "error": "Email address already exists. Please choose a different email."})
        
        # if all the above conditions are not true, it creates the user details to the db using create() method.
        my_user = User.objects.create(username=username, email=useremail)
        my_user.set_password(userpassword)
        my_user.save()
        login(request, my_user)
        return JsonResponse({"status":200, "message": "User registered successfully"})
    
    return render(request, 'register.html')

@csrf_exempt
def login_page(request):
    if request.method == 'POST':
        username = request.POST.get('username')
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
    visitor_data = NewVisitor.objects.filter(auth_user=request.user).order_by("id")
    checkout_count = ExitVisitor.objects.filter(auth_user=request.user).count()
    expected_visitor = InviteVisitor.objects.filter(auth_user=request.user).order_by("id")
    context = {
        'visitor_data': visitor_data,
        'checkout_count': checkout_count,
        'expected_visitor': expected_visitor,
    }
    return render(request, 'dashboard.html', context)


def logout_page(request):
    logout(request)
    return redirect('login')

@login_required(login_url='login')
def main_settings(request):
    data = Branches.objects.filter(auth_user=request.user).order_by("id") #auth_user=request.user - if the any user was loggedin, they can't see other users da 
    user_data = MainUser.objects.filter(auth_user=request.user)
    desk_data = Desk.objects.filter(auth_user=request.user)
    context = {
        'data':data,
        'user_data' :user_data,
        'desk_data' :desk_data,
    }

    return render(request, 'settings.html', context)

@login_required(login_url='login')
def visitors_page(request):
    data = Branches.objects.filter(auth_user=request.user)
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


def create_branch(request):
    if request.method == 'POST':
        name = request.POST.get("name").strip()
        branch_code = request.POST.get("branch_code").strip()

        if Branches.objects.filter(branch_code=branch_code, auth_user=request.user).exists():
            return JsonResponse({"status": 400, "type": "branch_code", "error": "Branch Code must be Unique"})
        
        country_code = request.POST.get("country_code").strip()
        timezone = request.POST.get("timezone")
        main_branch = Branches.objects.create(auth_user=request.user, name=name,
                                branch_code=branch_code, country_code=country_code,
                                timezone=timezone)
        created_branch_data = BranchSerializer(main_branch).data
        branch_data = Branches.objects.filter(auth_user=request.user)
        branch_data_count = branch_data.count()
        return JsonResponse({"status": 200, 'message': "Branch created", 'icon': 'success',
                            'created_branch_data': created_branch_data, 'branch_data_count': branch_data_count})
    

def delete(request):
    if request.method == 'POST':
        delete_id = request.POST.get("delete_id")
        delete_type = request.POST.get("delete_type")
        if delete_type == "user":
            user = MainUser.objects.get(id=delete_id)
            user.delete()
            return JsonResponse({'message': "User deleted successfully", 'icon': 'success'})
        if delete_type == 'branch':
            branch = Branches.objects.get(id=delete_id)
            branch.delete()
            return JsonResponse({'message': "Branch deleted successfully", 'icon': 'success','id': delete_id})
        if delete_type == 'desk':
            desk = Desk.objects.get(id=delete_id)
            desk.delete()
            return JsonResponse({'message': "Desk deleted successfully", 'icon': 'success', 'id': delete_id})
            


@login_required(login_url='login')
def user_info(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name').strip()
        last_name = request.POST.get('last_name').strip()
        user_email = request.POST.get('user_email').strip()     
        user_phone = request.POST.get('user_phone').strip()
        user_name = request.POST.get('user_name').strip()

        if MainUser.objects.filter(user_email=user_email).exists() and MainUser.objects.filter().exists():
            return JsonResponse({'status': 400, 'value': [{"status": 400, "type": "useremail", "error": "Email already exists. Please choose a different email."},
                                {"status": 400, "type": "username", "error": "Username already exists. Please use a different one."}]})

        elif MainUser.objects.filter(user_email=user_email).exists():
            return JsonResponse({'status': 400, 'type': "useremail", "error": "Email already exists. Please choose a different email." })
        
        elif MainUser.objects.filter(user_name=user_name).exists():
            return JsonResponse({"status": 400, "type": "username", "error": "Username already exists. Please use a different one."})

        # user_password = request.POST.get('user_password')
        user_role = request.POST.get('user_role')
        branch_id = request.POST.get('branch_id')
        
        if branch_id is None:
            return JsonResponse({'message': "Please select a branch", 'icon': 'error'})
        branch = Branches.objects.filter(pk=branch_id).first()

        # auth_user_data = User.objects.create_user(username=user_name, email=user_email, password=user_password)
        # auth_user_data.save()
        
        main_user = MainUser.objects.create(auth_user=request.user, first_name=first_name,
                                last_name=last_name, user_email=user_email,
                                user_phone=user_phone, user_name=user_name,
                                user_role=user_role,primary_branch=branch)
        
        created_data = UserSerializer(main_user).data
        user_data = MainUser.objects.filter(auth_user=request.user)
        user_data_count = user_data.count()
        return JsonResponse({"status": 200, 'message': "Successfully created user", 'icon': 'success', 'form_name': "user_info", "created_data": created_data,
                             'user_data_count': user_data_count})


def get_branch_counter(branch_name):
    try:
        branch = Branches.objects.get(name=branch_name)
        return branch.counter
    except Branches.DoesNotExist:
        return 1 
    

def update_branch_counter(branch_name, new_counter):
    branch, created = Branches.objects.get_or_create(name=branch_name)
    branch.counter = new_counter
    branch.save()


def generate_visitor_id(branch_name, branch_counter):
    branch_code = branch_name[:2].upper()
    branch_counter = get_branch_counter(branch_name)
    branch_counter += 1
    unique_id = f"{branch_code}{str(branch_counter).zfill(6)}"
    update_branch_counter(branch_name, branch_counter)
    return unique_id
    pass


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
        branch = Branches.objects.get(pk=branch_id)
        hosts = MainUser.objects.filter(primary_branch=branch)
        host_data = [{'id': host.id, 'name': f"{host.first_name} {host.last_name}"} for host in hosts]

        desks = Desk.objects.filter(select_branch=branch)
        desk_data = [{'id': desk.id, 'name': desk.desk_name} for desk in desks]
        return JsonResponse({'hosts': host_data,'desks': desk_data})
    else:
        return JsonResponse({'hosts': []}, {'desks': []})
    

@login_required(login_url='login')
def invite_visitor(request):
    if request.method == 'POST':
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
        branch = Branches.objects.filter(pk=branch_id).first()
        user_id = request.POST.get('user_id')

        if not user_id:
            return JsonResponse({"status": 400, "type": "userid", "error": "Select Host"})
       
        main_user = MainUser.objects.filter(pk=user_id).first()
        visitor_id = generate_visitor_id(branch.name, branch.counter)

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )

        qr.add_data(f"Check-in ID: {main_user.id}")
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        img_buffer = BytesIO()
        img.save(img_buffer, "png")
        img_buffer.seek(0)

        invitation_email(
                visitor_email, full_name, branch.name, f"{main_user.first_name} {main_user.last_name}", visitor_id, purpose, from_date, to_date, img_buffer.read()
            )
        
        invite_visitor = InviteVisitor.objects.create(purpose=purpose, auth_user=request.user, full_name=full_name, visitor_email=visitor_email,
            from_date=from_date, to_date=to_date, visitor_phone=visitor_phone, select_branch=branch, user_host=main_user, visitor_id=visitor_id)
        created_visitor_data = InviteVisitorSerializer(invite_visitor).data
        invite_visitor_data = InviteVisitor.objects.filter(auth_user=request.user)
        invite_visitor_data_count = invite_visitor_data.count()
        return JsonResponse({"status": 200, 'message': "Invited", 'icon': "success", 'form_name': 'invite_visitor',
                            'created_visitor_data': created_visitor_data, 'invite_visitor_data_count': invite_visitor_data_count})
    

@shared_task
def send_email_async(subject, message, from_email, recipient_list):
    send_mail(subject, message, from_email, recipient_list)


@login_required(login_url='login')
def add_desk(request):
    if request.method == 'POST':
        desk_name = request.POST.get('desk_name').strip()
        branch_id = request.POST.get('branch_id')

        if branch_id is None:
            return JsonResponse({"status": 400, "type": "desk_branchid", 'message': "Select Branch", 'icon': 'error'})
        branch = Branches.objects.filter(pk=branch_id).first()
        main_desk = Desk.objects.create(auth_user=request.user, desk_name=desk_name, select_branch=branch)
        created_desk_data = DeskSerializer(main_desk).data
        desk_data = Desk.objects.filter(auth_user=request.user)
        desk_data_count = desk_data.count()
        return JsonResponse({"status": 200, 'message': "Desk Created", 'icon': 'success', 'created_desk_data': created_desk_data, 'desk_data_count': desk_data_count})


@login_required(login_url='login')
def checkin_visitor(request):
    branch_data = Branches.objects.filter(auth_user=request.user)
    visitor_data = NewVisitor.objects.filter(auth_user=request.user)
    desk_data = Desk.objects.filter(auth_user=request.user)
    host_data = MainUser.objects.filter(auth_user=request.user)
    invited_visitor = InvitedVisitorCheck.objects.filter(auth_user=request.user)
    context = {
        'visitor_data': visitor_data,
        'branch_data': branch_data,
        'desk_data': desk_data,
        'host_data': host_data,
        'invited_visitor': invited_visitor,
    }
    return render(request, 'checkin.html', context)


@login_required(login_url='login')
def new_visitor(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name').strip()
        email = request.POST.get('email').strip()
        phone = request.POST.get('phone').strip()
        purpose = request.POST.get('purpose').strip()
        branch_id = request.POST.get('branch_id')

        errors = []
        if not branch_id:
            errors.append({'message': 'Select a branch', 'icon': 'error'})
        branch = Branches.objects.filter(pk=branch_id).first()
        desk_id = request.POST.get('desk_id')

        if not desk_id:
            errors.append({'message': 'Choose the desk', 'icon': 'error'})            
        desk = Desk.objects.filter(pk=desk_id).first()
        host_id = request.POST.get('host_id')
        
        if not host_id:
            errors.append({'message': 'Choose a host', 'icon': 'error'})
        host = MainUser.objects.filter(pk=host_id).first()

        if errors:
            return JsonResponse({'messages': errors, 'success': False})
        
        visitor_id = generate_visitor_id(branch.name, branch.counter)
        
        

        NewVisitor.objects.create(auth_user=request.user, full_name=full_name, email=email, phone=phone,
                                  purpose=purpose, select_branch=branch, user_host=host,
                                  select_desk=desk, visitor_id=visitor_id)
        return JsonResponse({'messages': [{'message': 'Added Successfully', 'icon': 'success'}], 'success': True})
    

    
@login_required(login_url='login')
def exit_visitor(request):
    if request.method == 'POST':
        exit_desk = request.POST.get('exit_desk')

        errors = []
        if not exit_desk:
            errors.append({'message': 'Desk is required', 'icon': 'error'})
        visitor_id = request.POST.get('visitor_id')
        try:
            visitor = NewVisitor.objects.get(visitor_id=visitor_id)
        except NewVisitor.DoesNotExist:
            errors.append({'message': 'Visitor not found', 'icon': 'error'})
        
        if visitor.checkout_time is not None:
            errors.append({'message': 'Visitor has already checked out', 'icon': 'error'})

        if errors:
            return JsonResponse({'messages': errors, 'success': False})
        
        exit_time = timezone.now()
        visitor_remarks = request.POST.get('visitor_remarks')
        
        visitor.checkout_time = exit_time  # Set the checkout time
        visitor.save()

        ExitVisitor.objects.create(auth_user=request.user, exit_desk_id=exit_desk,
                                   exit_time=exit_time, visitor_remarks=visitor_remarks)
        
        return JsonResponse({'messages': [{'message': 'Visitor checked out successfully', 'icon': 'success'}],
                             'checkout_time': exit_time.strftime('%Y-%m-%d %H:%M:%S'), 'success': True})


@login_required(login_url='login')
def append_checkout_modal(request):
    visitor_id = request.GET.get("id")
    vid = request.GET.get("vid")
    data = NewVisitor.objects.get(id=visitor_id)
    return render(request,'append_checkout_modal.html', {'data':data,'vid':vid})



@login_required(login_url='login')
def invited_visitor_check(request):
    if request.method == 'POST':
        visitor_id = request.POST.get('visitor_id')
        branch_id = request.POST.get('branch_id')
        
        try:
            branch = get_object_or_404(Branches, id=branch_id)
            visitor = get_object_or_404(InviteVisitor, visitor_id=visitor_id, select_branch=branch)
            invited_visitor_check, created = InvitedVisitorCheck.objects.get_or_create(
                visitor=visitor, invite_id=visitor_id, invited_visitor_branch=branch, auth_user=request.user
            )
            return JsonResponse({'message': 'Visitor details found', 'icon': 'success'})
        except:
            return JsonResponse({'message': 'Visitor not found', 'icon': 'error'})
    
    return render(request, 'checkin_visitor.html')
