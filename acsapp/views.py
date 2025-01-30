from django.shortcuts import render,redirect,get_object_or_404
from .models import *
from django.views.decorators.http import require_POST
from django.contrib.auth.models import User
from django.contrib.auth import login as auth_login, authenticate ,logout as auth_logout # Import login and rename it to auth_login
from django.contrib.auth.decorators import login_required
from django.urls import reverse
import re,pytz,os,json,csv
from django.utils.timesince import timesince
from django.http import JsonResponse,HttpResponse
from django.utils.dateformat import format
from django.utils.timezone import localtime
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import Group
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from datetime import datetime, timedelta
from django.db.models import Sum
from django.template.loader import render_to_string
from django.db.models import F



def components(req):
    return render(req,"components.html")

def createuserpage(req):
    return render(req,"createuserpage.html")

def todotable(request):
    project1 = Todolist.objects.all()
    print(project1,"this is test")
    return render(request,"todotable.html",{"project1":project1})

def create_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        User.objects.create_user(username=username, email=email, password=password)
        return redirect('admin:index')  # Redirects to the Django admin home / Redirect to the admin interface
    return render(request, 'create_user.html')

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        mobile = request.POST['mobile']
        password = request.POST['password']
        password2 = request.POST['cpassword']
        response = {'status': 'success'}
        
        # if not re.match(r'^[a-zA-Z0-9._%+-]+@gmail\.com$', email):
        #     response = {'status': 'error', 'message': 'Invalid email format. Email must end with @gmail.com'}
        #     return JsonResponse(response)
        
        if UserProfile.objects.filter(mobile=mobile).exists():
            response = {'status': 'error', 'message': 'Mobile number already in use'}
            return JsonResponse(response)
        
        # Check if mobile number is valid (e.g., length and numeric)
        if not re.match(r'^\d{10}$', mobile):
            response = {'status': 'error', 'message': 'Invalid mobile number. Must be 10 digits.'}
            return JsonResponse(response)
        
        if password != password2:
            response = {'status': 'error', 'message': 'Passwords do not match'}
            return JsonResponse(response)
        
        mobile = int(mobile)
        
        # Password validation
        # if len(password) < 8:
        #     response = {'status': 'error', 'message': 'Password must be at least 8 characters long'}
        #     return JsonResponse(response)

        # if not re.search(r'[A-Z]', password):
        #     response = {'status': 'error', 'message': 'Password must contain at least 1 uppercase letter'}
        #     return JsonResponse(response)

        # if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        #     response = {'status': 'error', 'message': 'Password must contain at least 1 special character'}
        #     return JsonResponse(response)

        # if not re.search(r'[0-9]', password):
        #     response = {'status': 'error', 'message': 'Password must contain at least 1 digit'}
        #     return JsonResponse(response)

        # if not re.search(r'[a-z]', password):
        #     response = {'status': 'error', 'message': 'Password must contain at least 1 lowercase letter'}
        #     return JsonResponse(response)

        if User.objects.filter(email=email).exists():
            response = {'status': 'error', 'message': 'Email already in use'}
            return JsonResponse(response)
        
        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()
        
        # Create user profile with mobile number
        user_profile = UserProfile.objects.create(user=user, mobile=mobile)
        user_profile.save()
        auth_logout(request)
        response = {
            'status': 'success',
            'message': 'Registration successful!',
            'redirect_url': reverse('login') 
        }
        return JsonResponse(response)

    return render(request, 'register.html')


def user_login(request):
    # Check if the user is already authenticated
    if request.user.is_authenticated:
        return redirect('members')  

    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        try:
            # Check if a user with the entered email exists
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Return an error response if email does not exist
            return JsonResponse({'status': 'error', 'message': 'No User Found'})

        # Authenticate using the username linked to the email
        user = authenticate(request, username=user.username, password=password)
        if user is not None:
            # If authentication is successful
            auth_login(request, user)
            request.session['login_success'] = True
            # request.session.set_expiry(900)  # Set session expiry to 15 minutes

            return JsonResponse({'status': 'success', 'redirect_url': reverse('dashboard')})
        else:
            # Return an error response if the password is incorrect
            return JsonResponse({'status': 'error', 'message': 'Invalid login credentials'})
    
    return render(request, 'login.html')




@login_required
def members(request):
    if request.user.is_authenticated:
        username = request.user.username
        return render(request, 'all_leads.html', {'username': username})
    else:
        return redirect('login')
  

def user_logout(request):
    if request.method == 'POST':
        # Store the user object before logging out
        user = request.user
        
        # Log the user out
        auth_logout(request)
        
        # Retrieve the last login record for the user
        last_login_record = LoginHistory.objects.filter(user=user).last()
        if last_login_record and not last_login_record.logout_time:
            last_login_record.logout_time = timezone.now()
            last_login_record.logout_reason = "manual"  # Reason for logout
            last_login_record.save()
        
        # Clear the session
        request.session.flush()
        
        # Redirect to the login page
        return redirect('login')
    
    return redirect('members')


@login_required
def tables(request):
    return render(request,"tables-data.html")


@login_required
def dashboard(req):
    # Exclude the currently logged-in user
    users = User.objects.exclude(id=req.user.id)

    # Default user is the currently logged-in user
    selected_user = req.user
    tasks = Task.objects.filter(user=selected_user)

    if req.method == 'POST':
        selected_user_id = req.POST.get('user_id')
        if selected_user_id:
            # Get tasks for the selected user
            selected_user = User.objects.get(id=selected_user_id)
            tasks = Task.objects.filter(user=selected_user)

    # Count users in each group
    superadmin_count = Group.objects.get(name="superadmin").user_set.count()
    admin_count = Group.objects.get(name="admin").user_set.count()
    normal_users_count = Group.objects.get(name="Normalusers").user_set.count()

    # Count tasks for the selected user by status
    not_started_count = tasks.filter(status='Not Started').count()
    working_count = tasks.filter(status='Working').count()
    # completed_count = tasks.filter(status='Completed', to_date__gte=F('updated_as_completed')).count()
    rework_count = tasks.filter(status='Rework').count()
    pending_review_count = tasks.filter(status='Pending Review').count()
    cancelled_count = tasks.filter(status='Cancelled').count()
    # Total completed tasks, including overdue and on-time
    # total_completed_tasks = tasks.filter(status='Completed').count()
     # Total completed tasks
    completed_tasks = tasks.filter(status='Completed')

    # Initialize counts
    overdue_completed_count = 0 
    normal_completed_count = 0

    for task in completed_tasks:
        if task.updated_as_completed and task.to_date:
            # Compare dates only, not the time
            if task.updated_as_completed.date() > task.to_date:
                overdue_completed_count += 1
            else:
                normal_completed_count += 1
        elif not task.updated_as_completed and task.to_date < timezone.now().date():
            # If the task is not marked as "Completed" and the `to_date` is in the past
            overdue_completed_count += 1


    # Pass data to the template
    context = {
        "users": users,
        "selected_user": selected_user,
        "superadmin_count": superadmin_count,
        "admin_count": admin_count,
        "normal_users_count": normal_users_count,
        "user_task_count": tasks.count(),
        "not_started_count": not_started_count,
        "working_count": working_count,
        "rework_count": rework_count,
        "pending_review_count": pending_review_count,
        "cancelled_count": cancelled_count,
        "total_completed_tasks": completed_tasks.count(),
        "overdue_completed_count": overdue_completed_count,
        "normal_completed_count": normal_completed_count,
    }
    return render(req, "dashboard.html", context)




def export_superadmins(request):
    # Get all superadmins
    superadmin_group = Group.objects.get(name="superadmin")
    superadmins = superadmin_group.user_set.all()

    # Create the HTTP response with CSV content
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="superadmins.csv"'

    # Write data to the CSV file
    writer = csv.writer(response)
    writer.writerow(['Username', 'Email', 'First Name', 'Last Name'])
    for user in superadmins:
        writer.writerow([user.username, user.email, user.first_name, user.last_name])

    return response


def export_admins(request):
    # Get all superadmins
    superadmin_group = Group.objects.get(name="Admin")
    superadmins = superadmin_group.user_set.all()

    # Create the HTTP response with CSV content
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="admins.csv"'

    # Write data to the CSV file
    writer = csv.writer(response)
    writer.writerow(['Username', 'Email', 'First Name', 'Last Name'])
    for user in superadmins:
        writer.writerow([user.username, user.email, user.first_name, user.last_name])

    return response


def export_users(request):
    # Get all superadmins
    superadmin_group = Group.objects.get(name="Normalusers")
    superadmins = superadmin_group.user_set.all()

    # Create the HTTP response with CSV content
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="users.csv"'

    # Write data to the CSV file
    writer = csv.writer(response)
    writer.writerow(['Username', 'Email', 'First Name', 'Last Name'])
    for user in superadmins:
        writer.writerow([user.username, user.email, user.first_name, user.last_name])

    return response



@login_required
def export_user_tasks(request):
    # Get the `user_id` from query parameters
    user_id = request.GET.get('user_id')
    if not user_id:
        return HttpResponse("User ID is required for exporting tasks.", status=400)

    # Get the selected user
    selected_user = get_object_or_404(User, id=user_id)

    # Filter tasks for the selected user
    user_tasks = Task.objects.filter(user=selected_user)

    # Create the HTTP response with CSV content
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{selected_user.username}_tasks.csv"'

    # Write data to the CSV file
    writer = csv.writer(response)
    writer.writerow(['Project Name', 'Task Name', 'Priority', 'From Date', 'To Date', 'Status', 'Description'])

    for task in user_tasks:
        writer.writerow([
            task.project.projectname if task.project else 'N/A',
            task.taskname,
            task.priority,
            task.from_date.strftime('%Y-%m-%d') if task.from_date else 'N/A',
            task.to_date.strftime('%Y-%m-%d') if task.to_date else 'N/A',
            task.status,
            task.description,
        ])

    return response


@login_required
def export_not_started_tasks(request):
    # Get the `user_id` from query parameters
    user_id = request.GET.get('user_id')
    if not user_id:
        return HttpResponse("User ID is required for exporting tasks.", status=400)

    # Get the selected user
    selected_user = get_object_or_404(User, id=user_id)

    # Filter "Not Started" tasks for the selected user
    not_started_tasks = Task.objects.filter(user=selected_user, status="Not Started")

    # Create the HTTP response with CSV content
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{selected_user.username}_not_started_tasks.csv"'

    # Write data to the CSV file
    writer = csv.writer(response)
    writer.writerow(['Project Name', 'Task Name','Priority', 'From Date', 'To Date', 'Status', 'Description'])

    for task in not_started_tasks:
        writer.writerow([
            task.project.projectname if task.project else 'N/A',
            task.taskname,
            # task.taskname,

            task.priority,
            task.from_date.strftime('%Y-%m-%d') if task.from_date else 'N/A',
            task.to_date.strftime('%Y-%m-%d') if task.to_date else 'N/A',
            task.status,
            task.description,
        ])

    return response



@login_required
def export_working_tasks(request):
    # Get the `user_id` from query parameters
    user_id = request.GET.get('user_id')
    if not user_id:
        return HttpResponse("User ID is required for exporting tasks.", status=400)

    # Get the selected user
    selected_user = get_object_or_404(User, id=user_id)

    # Filter "Not Started" tasks for the selected user
    not_started_tasks = Task.objects.filter(user=selected_user, status="Working")

    # Create the HTTP response with CSV content
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{selected_user.username}_Working_tasks.csv"'

    # Write data to the CSV file
    writer = csv.writer(response)
    writer.writerow(['Project Name', 'Task Name','Priority', 'From Date', 'To Date', 'Status', 'Description'])

    for task in not_started_tasks:
        writer.writerow([
            task.project.projectname if task.project else 'N/A',
            task.taskname,
            # task.taskname,

            task.priority,
            task.from_date.strftime('%Y-%m-%d') if task.from_date else 'N/A',
            task.to_date.strftime('%Y-%m-%d') if task.to_date else 'N/A',
            task.status,
            task.description,
        ])

    return response



@login_required
def export_completed_tasks(request):
    # Get the `user_id` from query parameters
    user_id = request.GET.get('user_id')
    if not user_id:
        return HttpResponse("User ID is required for exporting tasks.", status=400)

    # Get the selected user
    selected_user = get_object_or_404(User, id=user_id)

    # Filter "Not Started" tasks for the selected user
    not_started_tasks = Task.objects.filter(user=selected_user, status="Completed")

    # Create the HTTP response with CSV content
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{selected_user.username}_Completed_tasks.csv"'

    # Write data to the CSV file
    writer = csv.writer(response)
    writer.writerow(['Project Name', 'Task Name','Priority', 'From Date', 'To Date', 'Status', 'Description'])

    for task in not_started_tasks:
        writer.writerow([
            task.project.projectname if task.project else 'N/A',
            task.taskname,
            # task.taskname,

            task.priority,
            task.from_date.strftime('%Y-%m-%d') if task.from_date else 'N/A',
            task.to_date.strftime('%Y-%m-%d') if task.to_date else 'N/A',
            task.status,
            task.description,
        ])

    return response



@login_required
def export_ontime_completed_tasks(request):
    # Get the selected user's ID from the query parameters
    user_id = request.GET.get('user_id')
    print("vinotrh")
    
    # Ensure a user ID is provided
    if not user_id:
        return HttpResponse("User ID is required", status=400)
    
    try:
        # Get the selected user
        selected_user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return HttpResponse("User does not exist", status=404)

    # Fetch on-time completed tasks for the selected user
    tasks = Task.objects.filter(user=selected_user, status="Completed", to_date__gte=F('updated_as_completed'))

    # Create the HTTP response with CSV content type
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{selected_user.username}_Ontime_completed_tasks.csv"'

    # Write data to the CSV
    writer = csv.writer(response)
    writer.writerow(['Task Name', 'Status', 'Start Date', 'End Date', 'Updated as Completed'])

    for task in tasks:
        writer.writerow([task.taskname, task.status, task.from_date, task.to_date, task.updated_as_completed])

    return response



def export_overdue_completed_tasks(request):
    # Get the user ID from the query parameters
    user_id = request.GET.get('user_id')

    # Check if the user ID is provided
    if not user_id:
        return HttpResponse("User ID is required", status=400)

    # Validate if the user exists
    try:
        selected_user = User.objects.get(id=user_id)  # Replace `User` with your user model
    except User.DoesNotExist:
        return HttpResponse("User does not exist", status=404)

    # Query for overdue completed tasks
    tasks = Task.objects.filter(
        user=selected_user,
        status="Completed",
        to_date__lt=F('updated_as_completed')  # Adjust this filter based on your logic for overdue tasks
    )

    # Create the CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{selected_user.username}_overdue_completed_tasks.csv"'

    # Write to the CSV
    writer = csv.writer(response)
    writer.writerow(['Task ID', 'Task Name', 'Status', 'Priority', 'Start Date', 'Due Date', 'Completion Date'])

    for task in tasks:
        writer.writerow([
            # task.id,
            task.taskname,  # Corrected field name
            task.status,
            task.priority,
            task.from_date,
            task.to_date,
            task.updated_as_completed,
        ])

    return response


import csv
from django.http import HttpResponse
from .models import Task

def export_total_completed_tasks(request):
    # Get the user ID from the query parameters
    user_id = request.GET.get('user_id')

    # Check if the user ID is provided
    if not user_id:
        return HttpResponse("User ID is required", status=400)

    # Validate if the user exists
    try:
        selected_user = User.objects.get(id=user_id)  # Replace `User` with your user model
    except User.DoesNotExist:
        return HttpResponse("User does not exist", status=404)

    # Query for total completed tasks
    tasks = Task.objects.filter(user=selected_user, status="Completed")

    # Create the CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{selected_user.username}_total_completed_tasks.csv"'

    # Write to the CSV
    writer = csv.writer(response)
    writer.writerow(['Task Name', 'Status', 'Priority', 'Start Date', 'Due Date', 'Completion Date'])

    for task in tasks:
        writer.writerow([
            task.taskname,  # Task name field
            task.status,
            task.priority,
            task.from_date,
            task.to_date,
            task.updated_as_completed,  # Completion date field
        ])

    return response



@login_required
def export_rework_tasks(request):
    # Get the `user_id` from query parameters
    user_id = request.GET.get('user_id')
    if not user_id:
        return HttpResponse("User ID is required for exporting tasks.", status=400)

    # Get the selected user
    selected_user = get_object_or_404(User, id=user_id)

    # Filter "Not Started" tasks for the selected user
    not_started_tasks = Task.objects.filter(user=selected_user, status="Rework")

    # Create the HTTP response with CSV content
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{selected_user.username}_Rework_tasks.csv"'

    # Write data to the CSV file
    writer = csv.writer(response)
    writer.writerow(['Project Name', 'Task Name','Priority', 'From Date', 'To Date', 'Status', 'Description'])

    for task in not_started_tasks:
        writer.writerow([
            task.project.projectname if task.project else 'N/A',
            task.taskname,
            # task.taskname,

            task.priority,
            task.from_date.strftime('%Y-%m-%d') if task.from_date else 'N/A',
            task.to_date.strftime('%Y-%m-%d') if task.to_date else 'N/A',
            task.status,
            task.description,
        ])

    return response




@login_required
def export_pending_review_tasks(request):
    # Get the `user_id` from query parameters
    user_id = request.GET.get('user_id')
    if not user_id:
        return HttpResponse("User ID is required for exporting tasks.", status=400)

    # Get the selected user
    selected_user = get_object_or_404(User, id=user_id)

    # Filter "Not Started" tasks for the selected user
    not_started_tasks = Task.objects.filter(user=selected_user, status="Pending Review")

    # Create the HTTP response with CSV content
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{selected_user.username}_pending_review_tasks.csv"'

    # Write data to the CSV file
    writer = csv.writer(response)
    writer.writerow(['Project Name', 'Task Name','Priority', 'From Date', 'To Date', 'Status', 'Description'])

    for task in not_started_tasks:
        writer.writerow([
            task.project.projectname if task.project else 'N/A',
            task.taskname,
            # task.taskname,

            task.priority,
            task.from_date.strftime('%Y-%m-%d') if task.from_date else 'N/A',
            task.to_date.strftime('%Y-%m-%d') if task.to_date else 'N/A',
            task.status,
            task.description,
        ])

    return response



@login_required
def export_cancelled_tasks(request):
    # Get the `user_id` from query parameters
    user_id = request.GET.get('user_id')
    if not user_id:
        return HttpResponse("User ID is required for exporting tasks.", status=400)

    # Get the selected user
    selected_user = get_object_or_404(User, id=user_id)

    # Filter "Not Started" tasks for the selected user
    not_started_tasks = Task.objects.filter(user=selected_user, status="Cancelled")

    # Create the HTTP response with CSV content
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{selected_user.username}_cancelled_tasks.csv"'

    # Write data to the CSV file
    writer = csv.writer(response)
    writer.writerow(['Project Name', 'Task Name','Priority', 'From Date', 'To Date', 'Status', 'Description'])

    for task in not_started_tasks:
        writer.writerow([
            task.project.projectname if task.project else 'N/A',
            task.taskname,
            # task.taskname,

            task.priority,
            task.from_date.strftime('%Y-%m-%d') if task.from_date else 'N/A',
            task.to_date.strftime('%Y-%m-%d') if task.to_date else 'N/A',
            task.status,
            task.description,
        ])

    return response


@login_required
def allusersview(req, group_name):
    try:
        # Get the group
        group = Group.objects.get(name=group_name)

        # Get all users in the group
        users = group.user_set.all()
    except Group.DoesNotExist:
        # Handle group not found
        users = []

    context = {
        "group_name": group_name,
        "users": users,
    }
    return render(req, "allusersview.html", context)

def tasks_view(request, user_id):
    print("ftyuijhuycfgy")
    user = User.objects.get(id=user_id)
    tasks = Task.objects.filter(user=user)
    # not_started_tasks = all_tasks.filter(status="Not Started")


    context = {
        'tasks': tasks,
        'user': user,
    }
    return render(request, 'taskview.html', context)


def dashboardtaskview(request, user_id=None, status=None):
    user = User.objects.get(id=user_id) if user_id else request.user
    tasks = Task.objects.filter(user=user)

    # Initialize counts and filtered tasks
    normal_completed_tasks = []
    overdue_completed_tasks = []
    total_completed_tasks = []
    not_started_tasks = []
    rework_tasks = []  # For rework tasks
    pending_review_tasks = []  # For pending review tasks
    cancelled_tasks = []  # For cancelled tasks
    working_tasks = []  # For working tasks

    normal_completed_count = 0
    overdue_completed_count = 0
    total_completed_count = 0
    not_started_count = 0
    rework_count = 0  # For rework tasks
    pending_review_count = 0  # For pending review tasks
    cancelled_count = 0  # For cancelled tasks
    working_count = 0  # For working tasks

    # Filter completed tasks
    completed_tasks = tasks.filter(status="Completed")

    # Calculate counts and filter the tasks to show
    for task in completed_tasks:
        if task.updated_as_completed and task.to_date:
            if task.updated_as_completed.date() > task.to_date:
                overdue_completed_count += 1
                overdue_completed_tasks.append(task)
            else:
                normal_completed_count += 1
                normal_completed_tasks.append(task)
        
        total_completed_count += 1
        total_completed_tasks.append(task)

    # Filter tasks based on other statuses
    not_started_tasks = tasks.filter(status="Not Started")
    rework_tasks = tasks.filter(status="Rework")
    pending_review_tasks = tasks.filter(status="Pending Review")
    cancelled_tasks = tasks.filter(status="Cancelled")
    working_tasks = tasks.filter(status="Working")  # New filter for working tasks

    not_started_count = not_started_tasks.count()
    rework_count = rework_tasks.count()
    pending_review_count = pending_review_tasks.count()
    cancelled_count = cancelled_tasks.count()
    working_count = working_tasks.count()  # Count for working tasks

    # Filter tasks based on the 'status' passed in the URL
    if status == "Not Started":
        tasks = not_started_tasks
    elif status == "Rework":
        tasks = rework_tasks
    elif status == "Pending Review":
        tasks = pending_review_tasks
    elif status == "Cancelled":
        tasks = cancelled_tasks
    elif status == "ontime":
        tasks = normal_completed_tasks
    elif status == "overdue_completed":
        tasks = overdue_completed_tasks
    elif status == "total_completed":
        tasks = total_completed_tasks
    elif status == "working":
        tasks = working_tasks  # Filtered working tasks

    context = {
        'tasks': tasks,
        'user': user,
        'status': status,
        'total_completed_count': total_completed_count,
        'normal_completed_count': normal_completed_count,
        'overdue_completed_count': overdue_completed_count,
        'not_started_count': not_started_count,
        'rework_count': rework_count,
        'pending_review_count': pending_review_count,
        'cancelled_count': cancelled_count,
        'working_count': working_count,  # Pass the count for working tasks
        'normal_completed_tasks': normal_completed_tasks,
        'overdue_completed_tasks': overdue_completed_tasks,
        'total_completed_tasks': total_completed_tasks,
        'not_started_tasks': not_started_tasks,
        'rework_tasks': rework_tasks,
        'pending_review_tasks': pending_review_tasks,
        'cancelled_tasks': cancelled_tasks,
        'working_tasks': working_tasks,  # Add working tasks to context
    }

    return render(request, 'taskview.html', context)
def custom_admin(request):
    return render(request,"custom_admin.html")
@login_required
def todlistpage(request):


    print("todolistpage function")

    if request.user.groups.filter(name="SuperAdmin").exists():
        # For SuperAdmin, fetch projects where the 'user' field is the logged-in user's ID
        projects = Project.objects.filter(user=request.user).distinct().order_by('-created_at')
        print("SuperAdmin projects:", projects)
    else:
        # For regular users, fetch projects that have tasks assigned to the logged-in user
        projects = Project.objects.filter(tasks__user=request.user).distinct().order_by('-created_at')
        print("Regular user projects:", projects)

    # Iterate through the projects and check the status of tasks
    for project in projects:
        # Check if all tasks for this project are completed
        if project.all_tasks_completed():
            print("Project all tasks completed")
            # Update the project status to 'Completed' if all tasks are completed
            if project.status != 'completed':
                project.status = 'completed'
                project.save()  # Save the updated status
        else:
            print("Project not all tasks completed")
            # Set project status to 'Pending Review' if not all tasks are completed
            if project.status != 'pending_review':
                project.status = 'pending_review'
                project.save()

    # Only show 'Pending' and 'Completed' as status choices for display purposes
    status_choices = [('pending_review', 'Pending'), ('completed', 'Completed')]
    print("Final project list:", projects)

    return render(request, 'todopage.html', {'projects': projects, 'status_choices': status_choices})


@require_POST
def update_status(request, project_id):
    status_value = request.POST.get('status')
    project = get_object_or_404(Project, id=project_id)
    if status_value in dict(Project.STATUS_CHOICES).keys():  # Validate status
        project.status = status_value
        project.save()
    return redirect('todlistpage') # Redirect to the project list page after saving as needed

def todopgt(request):
     print("pgt function")
     if request.method == 'POST':
        projectname = request.POST.get('projectname')
        projectenddate = request.POST.get('projectdate')
        projectstatus = request.POST.get('projectpriority')
        if Project.objects.filter(projectname=projectname).exists():
            return JsonResponse({'status': 'error', 'message': 'Project name already exists.'})

        print(projectname)
        if projectname:
            print("pgt if")
            # Create and save the project
            Project.objects.create(
                projectname=projectname,
                to_date=projectenddate,
                priority=projectstatus,
                user=request.user,  # Assign the currently logged-in user
                assigned_by=request.user  # Assign the currently logged-in user as the creator

            )
            print("project saved")
            return redirect('todlistpage')  # Redirect to the project list page after saving
     return render(request,"todolist.html")


@login_required
def projects(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    
    # Retrieve all tasks related to the project and categorize them by status
    todo_tasks = project.details.filter(status='todo')
    in_progress_tasks = project.details.filter(status='in_progress')
    done_tasks = project.details.filter(status='done')

    # Combine project details and comments into one list (if needed for something else)
    combined_list = list(todo_tasks) + list(in_progress_tasks) + list(done_tasks)
    combined_list.sort(key=lambda x: x.created_at, reverse=True)

    # Calculate time ago for each task
    for item in combined_list:
        item.time_ago = timesince(item.created_at).split(', ')[-1]

    # Pass the categorized tasks to the template
    return render(request, 'todolist.html', {
        'project': project,
        'todo_tasks': todo_tasks,
        'in_progress_tasks': in_progress_tasks,
        'done_tasks': done_tasks,
    })


@csrf_exempt
def delete_project(request, project_id):
    if request.method == 'POST' or 'GET':
        project = get_object_or_404(Project, id=project_id)

        # Archive the project details
        deleted_at_utc = timezone.now()  # Get the current time in UTC
        deleted_at_local = timezone.localtime(deleted_at_utc)

        archived_project = ArchivedProject(
            projectname=project.projectname,
            priority=project.priority,
            from_date=project.from_date,
            to_date=project.to_date,
            created_at=project.created_at,
            updated_at=project.updated_at,
            deleted_at=deleted_at_local,  # Set the deletion date and time
            user=project.user,
            assigned_by=project.assigned_by,
            status=project.status,
        )
        archived_project.save()

        # Delete the original project
        project.delete()

        return JsonResponse({'message': 'Project deleted successfully'}, status=200)

    return JsonResponse({'error': 'Invalid request method'}, status=400)

# # DELETE THIS FUNCTION
# def create_issue(request, project_id):
#     project = get_object_or_404(Project, id=project_id)
    
#     if request.method == 'POST':
#         issuename = request.POST.get('issuename')
#         print(issuename)
#         if issuename:
#             print("if",issuename)
#             Issue.objects.create(project=project, title=issuename, description=issuename)
#             return redirect('projects', project_id=project.id)
    
#     return render(request, 'todolist.html', {'project': project})



# # DELETE THIS FUNCTION
# def edit_issue(request, issue_id):
#     issue = get_object_or_404(Issue, id=issue_id)
    
#     if request.method == 'POST':
#         issue.description = request.POST.get('description')
#         issue.save()
        
#         return redirect('projects', project_id=issue.project.id)  # Redirect to the project's issues view

#     return render(request, 'edit_issue.html', {'issue': issue})

# # DELETE THIS FUNCTION
# @require_POST
# def delete_issue(request, issue_id):
#     print("print delete issue")
#     issue = get_object_or_404(Issue, id=issue_id)
#     project_id = issue.project.id  # Capture the project ID before deleting
#     issue.delete()
#     return redirect('projects', project_id=project_id)  # Redirect to the projects view after deletion

from django.utils.timezone import localtime, now

def card_update_task_status(request, task_id):
    task = get_object_or_404(Task, id=task_id)

    if request.method == 'POST':
        status = request.POST.get('status')

        # Ensure the provided status is valid
        if status in dict(Task.STATUS_CHOICES).keys() and task.status != status:
            # Update task status and timestamp
            task.status = status
            task.status_updated_at = now()
            task.save()

            # Identify the current user (the one performing the action)
            current_user = request.user

            # Notify the assigned user, if not the current user
            if task.user != current_user:
                Notification.objects.create(
                    user=task.user,
                    message=f"Your task '{task.taskname}' status was changed to {status} by '{current_user}'.",
                    assigned_by=current_user
                )

            # Notify the assigner, if not the current user and not the assigned user
            if task.assigned_by and task.assigned_by != current_user and task.assigned_by != task.user:
                Notification.objects.create(
                    user=task.assigned_by,
                    message=f"The task '{task.taskname}' assigned to {task.user.username} was updated to {status}.",
                    assigned_by=current_user
                )

    # Redirect to the same page (current page)
    return redirect(request.META.get('HTTP_REFERER', 'all_projects_with_tasks'))
     

        
    
# def fetch_status_notifications(request):
#     user = request.user
#     # Filter notifications that are related to status updates only
#     status_notifications = Notificationstatus.objects.filter(user=user, notification_type=Notificationstatus.STATUS_UPDATED).order_by('-created_at')
#     kolkata_tz = pytz.timezone('Asia/Kolkata')

#     # Prepare the data for the response
#     notification_data = [{
#         'assigned_by': Notificationstatus.assigned_by.username,
#         'message': Notificationstatus.message,  # Status update message
#         'created_at': Notificationstatus.created_at.astimezone(kolkata_tz).strftime('%Y-%m-%d %I:%M %p'),
#     } for notification in status_notifications]

#     unread_count = Notification.objects.filter(user=user, is_read=False, notification_type=Notification.STATUS_UPDATED).count()

#     return JsonResponse({'notifications': notification_data, 'unread_count': unread_count})




    


# DELETE THIS FUNCTION
def create_todolist(request, project_id):
    print("Entered create_todolist view")
    project = get_object_or_404(Project, id=project_id)

    if request.method == 'POST':
        print("POST method detected")
        description = request.POST.get('description')
        comments = request.POST.get('comments')
        # status = request.POST.get('status')

        # print("this is status",status)

        
        # Get the list of attached files
        attached_files = request.FILES.getlist('attached_file[]')

        # # Check if total file size exceeds 25 MB
        # max_file_size = 25 * 1024 * 1024  # 25 MB in bytes
        # total_file_size = sum(file.size for file in attached_files)

       
       

        print(f"Description: {description}")
        print(f"Comments: {comments}")
        print(f"Attached Files: {attached_files}")
        # print(f"status: {status}")

        
        if attached_files:
            for file in attached_files:
                print(f"Processing file: {file.name}")

        if description:
            todolist = Todolist(
                project=project,
                description=description,
                comments=comments,
                # status=status,

                user=request.user
            )
            todolist.save()

            print("data saved ")

            for attached_file in attached_files:
                TodolistFile.objects.create(
                    todolist=todolist,
                    attached_file=attached_file
                )
                print(f"Saved file: {attached_file.name}")

            print("New data and files saved successfully")
            return redirect('projects', project_id=project.id)
        else:
            print("No description provided")

    return render(request, 'todolist.html', {'project': project})


def fetch_all_data(request):
    print("fetching all data")

    # Fetch all projects and tasks
    projects = Project.objects.all()
    todotasks = Todolist.objects.all()

    # Serialize project data
    data = []
    for project in projects:
        data.append({
            'id': project.id,
            'title': f"Project: {project.projectname}",  # Ensure projectname is the correct field
            'created_at': format(project.created_at, 'Y-m-dTH:i:sZ'),
        })

    # Serialize task data
    for task in todotasks:
        data.append({
            'id': task.id,
            'title': f"Comment for {task.project.projectname}",  # Use the correct field name
            'created_at': format(task.created_at, 'Y-m-dTH:i:sZ'),
            'description': task.description,  # Include the description field if needed
        })

    return JsonResponse(data, safe=False)


@login_required
def user_list(request):
    if request.user.groups.filter(name__in=["Admin", "SuperAdmin"]).exists():
        # Fetch all users excluding superusers (but include the logged-in Admin)
        superadmin_group = Group.objects.get(name='Superadmin')

# Exclude users who are in the "Superadmin" group
        users = User.objects.exclude(groups=superadmin_group)        
        return render(request, 'user_list.html', {'users': users})
    else:
        # Redirect non-superusers or show a permission denied message
        return JsonResponse({'error': 'Permission Denied'}, status=403)  


@login_required
def user_list(request):
    if request.user.groups.filter(name__in=["Admin", "SuperAdmin"]).exists():
        # Fetch all users excluding superusers (but include the logged-in Admin)
        superadmin_group = Group.objects.get(name='Superadmin')
        users = User.objects.exclude(groups=superadmin_group)

        today = timezone.now().date()

        
        # Add the latest login and logout time to each user
        for user in users:
            latest_login = LoginHistory.objects.filter(user=user, login_time__isnull=False).order_by('-login_time').first()
            latest_logout = LoginHistory.objects.filter(user=user, logout_time__isnull=False).order_by('-logout_time').first()

            # Dynamically add latest login and logout to the user instance
            user.latest_login = latest_login.login_time if latest_login else None
            user.latest_logout = latest_logout.logout_time if latest_logout else None

              # Calculate total logged-in hours for today
            today_logins = LoginHistory.objects.filter(
                user=user,
                login_time__date=today
            )

            total_seconds = 0
            for record in today_logins:
                if record.logout_time:
                    total_seconds += (record.logout_time - record.login_time).total_seconds()

            user.total_hours_today = round(total_seconds / 3600, 2)  # Convert to hours and round
        
        # Render the user list page with the users and their login/logout times
        return render(request, 'user_list.html', {'users': users})
    else:
        # Redirect non-superusers or show a permission denied message
        return JsonResponse({'error': 'Permission Denied'}, status=403)
  

def loginusers(request):
    # Fetch all users
    users = User.objects.all()
    return render(request, "loginusers.html", {"users": users})



@csrf_exempt  # Remove this in production if CSRF tokeans are properly included
def get_user_login_history(request):
    print("Function called")  # Debugging log
    if request.method == "POST":
        user_id = request.POST.get("user_id")
        print(f"Received user_id: {user_id}")  # Debugging log
        if user_id:
            # Get today's date in Kolkata timezone
            kolkata_timezone = pytz.timezone('Asia/Kolkata')
            today = timezone.now().astimezone(kolkata_timezone).date()

            # Define the start and end of today's date
            start_of_day = timezone.datetime.combine(today, timezone.datetime.min.time(), tzinfo=kolkata_timezone)
            end_of_day = timezone.datetime.combine(today, timezone.datetime.max.time(), tzinfo=kolkata_timezone)

            # Filter login history by user_id and today's date range (from start of the day to the end of the day)
            login_history = LoginHistory.objects.filter(
                user_id=user_id,
                login_time__range=(start_of_day, end_of_day)  # Filter by today's date range
            ).order_by('-login_time')
            print(f"Login history for today: {login_history}")  # Debugging log
            
            total_time = 0  # Initialize total time in seconds

            # Prepare data with formatted login and logout times in Kolkata timezone
            data = []
            for entry in login_history:
                login_time = entry.login_time.astimezone(kolkata_timezone)
                logout_time = entry.logout_time.astimezone(kolkata_timezone) if entry.logout_time else None

                # Calculate session duration in seconds
                if logout_time:
                    session_duration = (logout_time - login_time).total_seconds()
                    total_time += session_duration
                    logout_time_str = logout_time.strftime("%d-%m-%Y %H:%M:%S")
                else:
                    session_duration = 0
                    logout_time_str = "Currently logged in"

                # Add entry data
                data.append({
                    "login_time": login_time.strftime("%d-%m-%Y %H:%M:%S"),
                    "logout_time": logout_time_str,
                    "session_duration": session_duration / 3600  # Convert seconds to hours
                })

            # Convert total time (in seconds) to HH:MM:SS format
            hours, remainder = divmod(total_time, 3600)
            minutes, seconds = divmod(remainder, 60)
            total_time_formatted = f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"
            
            print(f"Total time spent today: {total_time_formatted}")  # Debugging log

            # Return login data and formatted total time
            return JsonResponse({
                "success": True,
                "data": data,
                "total_time": total_time_formatted
            })
        
        return JsonResponse({"success": False, "error": "User ID not provided"})
    
    return JsonResponse({"success": False, "error": "Invalid request"})


@csrf_exempt
def filter_login_history_by_date(request):
    print("Function called")  # Debugging log
    if request.method == "POST":
        user_id = request.POST.get("user_id")
        selected_date = request.POST.get("selected_date")

        print(f"Received user_id: {user_id}, selected_date: {selected_date}")  # Debugging log

        if user_id and selected_date:
            # Get the selected date in Kolkata timezone
            kolkata_timezone = pytz.timezone('Asia/Kolkata')
            selected_date = timezone.datetime.strptime(selected_date, '%Y-%m-%d').date()

            # Define the start and end of the selected date
            start_of_day = timezone.datetime.combine(selected_date, timezone.datetime.min.time(), tzinfo=kolkata_timezone)
            end_of_day = timezone.datetime.combine(selected_date, timezone.datetime.max.time(), tzinfo=kolkata_timezone)

            # Filter login history by user_id and the selected date range (from start of the day to the end of the day)
            login_history = LoginHistory.objects.filter(
                user_id=user_id,
                login_time__range=(start_of_day, end_of_day)  # Filter by selected date range
            ).order_by('-login_time')

            # Calculate total time spent today
            total_time_spent = timedelta()

            data = []
            for entry in login_history:
                login_time = entry.login_time.astimezone(kolkata_timezone)
                logout_time = entry.logout_time.astimezone(kolkata_timezone) if entry.logout_time else None

                # Calculate time spent for this session
                if logout_time:
                    time_spent = logout_time - login_time
                else:
                    time_spent = timezone.now() - login_time  # Time spent until now if still logged in

                total_time_spent += time_spent

                data.append({
                    "login_time": login_time.strftime("%d-%m-%Y %H:%M:%S"),
                    "logout_time": (logout_time.strftime("%d-%m-%Y %H:%M:%S") 
                                    if logout_time else "Currently logged in"),
                    "time_spent": str(time_spent).split(".")[0]  # Show in HH:MM:SS format
                })

            # Format total time spent in HH:MM:SS
            total_hours, remainder = divmod(total_time_spent.seconds, 3600)
            total_minutes, total_seconds = divmod(remainder, 60)
            total_time_formatted = f"{total_hours:02}:{total_minutes:02}:{total_seconds:02}"

            print(f"Login history data: {data}")  # Debugging log
            return JsonResponse({"success": True, "data": data, "total_time": total_time_formatted})
        
        return JsonResponse({"success": False, "error": "User ID or Date not provided"})
    
    return JsonResponse({"success": False, "error": "Invalid request"})


@csrf_exempt
def save_logout_time(request):
    if request.method == "POST" and request.user.is_authenticated:
        logout_reason = request.POST.get("reason", "unknown")  # Get logout reason
        try:
            last_login_record = LoginHistory.objects.filter(user=request.user).last()
            if last_login_record and not last_login_record.logout_time:
                kolkata_timezone = pytz.timezone('Asia/Kolkata')
                logout_time_utc = timezone.now()
                logout_time_local = logout_time_utc.astimezone(kolkata_timezone)

                # Save logout time and reason
                last_login_record.logout_time = logout_time_utc
                last_login_record.logout_reason = logout_reason
                last_login_record.save()

                return JsonResponse({"success": True, "message": "Logout time saved successfully."})
            return JsonResponse({"success": False, "message": "No active session found."})
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})
    return JsonResponse({"success": False, "message": "Invalid request."})

    

@login_required
def delete_user(request, user_id):
    if request.user.is_superuser:
        # user = get_object_or_404(User, id=user_id)
        
        # # Archive the user details before deletion
        # ArchivedUser.objects.create(
        #     username=user.username,
        #     email=user.email,
        #     date_joined=user.date_joined
        # )
        
        # # Delete the user
        # user.delete()

        user_to_delete = User.objects.get(pk=user_id)
        object_repr = str(user_to_delete)  # Representation of the object being deleted
        user_to_delete.delete()

        # Log the deletion
        ActionLog.objects.create(
            user=request.user,  # The user performing the deletion
            action='DELETE',
            model_name='User',
            object_id=user_id,
            object_repr=object_repr
        )
            
        return JsonResponse({'success': 'User deleted successfully.'})
    else:
        return JsonResponse({'error': 'Permission Denied'}, status=403)


def create_project(request):
    print("create_project function")

    if request.method == 'POST':
        # Get form data from POST request
        projectname = request.POST.get('projectname')
        taskname = request.POST.get('taskname')
        priority = request.POST.get('priority')
        from_date = request.POST.get('fromdate')
        to_date = request.POST.get('todate')
        # default_user = get_object_or_404(User, username='Punithan')

        if Project.objects.filter(projectname=projectname).exists():
            return JsonResponse({'status': 'error', 'message': 'Project name already exists, please give a different name'})

        try:
            print("try block")
            # Create and save new Project instance
            project = Project(
                projectname=projectname,
                priority=priority,
                from_date=from_date,
                to_date=to_date,
                assigned_by=request.user,  # Set the user creating the project
                user=None, 
            )
            project.save()
            print("Project data saved")

            # Redirect back to the user's project page
            return redirect('user_project')

        except Exception as e:
            print("except")
            return HttpResponse(f"An error occurred: {e}", status=500)

    return render(request, 'create_project.html')

def loginerror(req):
    return render(req,"loginerror.html")


def user_project(request):
    print("user_project function")

    # Get all projects excluding SuperAdmin-related projects
    user_projects = Project.objects.exclude(user__groups__name='SuperAdmin').order_by('-created_at')
    print("Filtered user_projects (excluding SuperAdmin projects):", user_projects)

    context = {
        'projects': user_projects,  # Pass all filtered projects
    }

    return render(request, 'user_project.html', context)






def edit_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    
    if request.method == 'POST':
        project.projectname = request.POST.get('projectname')
        project.taskname = request.POST.get('taskname')
        project.priority = request.POST.get('priority')
        project.from_date = request.POST.get('fromdate')
        project.to_date = request.POST.get('todate')
        
        project.save()
        return redirect('todlistpage')
    
    return HttpResponse("Invalid request method.", status=400)



    


@login_required
def assigned_projects_view(request):
    if request.user.is_authenticated:
        # Fetch projects assigned to the currently logged-in user
        projects = Project.objects.filter(user=request.user)
        print(projects,"username")
    else:
        projects = Project.objects.none()  # No projects if not authenticated
        print(projects,"username else")


    context = {
        'projects': projects
    }
    return render(request, 'todopage.html', context)

@csrf_exempt
def update_task_status(request, task_id):
    if request.method == 'POST':
        try:
            # Parse the request body to get the new status
            data = json.loads(request.body)
            new_status = data.get('status')

            # Fetch the task using the Task model
            task = Task.objects.get(id=task_id)

            # Ensure the new status is different before updating
            if task.status != new_status:
                # Update the task's status and status_updated_at
                task.status = new_status
                task.status_updated_at = now()
                task.save()

                # Identify the current user (the one performing the action)
                current_user = request.user

                # Notify the assigned user, if not the current user
                if task.user != current_user:
                    Notification.objects.create(
                        user=task.user,
                        message=f"Your task '{task.taskname}' status was changed to {new_status} by '{current_user}'.",
                        assigned_by=current_user
                    )

                # Notify the assigner, if not the current user and not the assigned user
                if task.assigned_by and task.assigned_by != current_user and task.assigned_by != task.user:
                    Notification.objects.create(
                        user=task.assigned_by,
                        message=f"The task '{task.taskname}' assigned to {task.user.username} was updated to {new_status}.",
                        assigned_by=current_user
                    )

            # Return a success response
            return JsonResponse({'success': True})

        except Task.DoesNotExist:
            return JsonResponse({'error': 'Task not found'}, status=404)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    # Return an error response if the request method is not POST
    return JsonResponse({'error': 'Invalid request method'}, status=400)



def task_view(request):
    todotasks = Todolist.objects.filter(status='todo')
    in_progress_tasks = Todolist.objects.filter(status='in_progress')
    done = Todolist.objects.filter(status='done')

    context = {
        'todotask': todotasks,
        'in_progress_tasks': in_progress_tasks,
    }

    return render(request, 'todolist.html', context)

def task_detail(request, project_id):
    project = Project.objects.get(id=project_id)
    tasks = Task.objects.filter(project=project)  # Fetch all tasks for the project

    # Fetch all tasks related to this project for parent task dropdown
    all_tasks = Task.objects.filter(project=project)
    superadmin_group = Group.objects.get(name='Superadmin')
    excluded_users = User.objects.filter(groups=superadmin_group)
    available_users = User.objects.exclude(id__in=excluded_users.values_list('id', flat=True))

    return render(request, 'task_detail.html', {
        'tasks': tasks,
        'selected_project': project,
        'all_tasks': all_tasks,  # Passing all tasks for parent task selection
        'available_users': available_users
    })




from django.contrib.auth.models import User

from django.core.mail import send_mail
from django.conf import settings

from django.core.exceptions import ValidationError
from django.contrib import messages

def create_task(request, project_id):
    if request.method == 'POST':
        project = get_object_or_404(Project, id=project_id)

        # Get task details from the POST request
        taskname = request.POST.get('taskname')
        priority = request.POST.get('priority')
        from_date = request.POST.get('fromdate')
        to_date = request.POST.get('todate')
        description = request.POST.get('description')
        is_child = request.POST.get('is_child') == 'on'
        parent_task_id = request.POST.get('parent_task')

        if is_child and not parent_task_id:
            messages.error(request, "Please select a parent task when 'Is Child' is checked.")
            return redirect(request.META.get('HTTP_REFERER', '/'))

        # Get selected users from the POST request
        selected_user_ids = request.POST.getlist('selected_users')
        selected_users = User.objects.filter(id__in=selected_user_ids)

        if not selected_users:
            # Handle case where no users are selected
            messages.error(request, "Please select at least one user to assign the task.")
            return redirect('create_task', project_id=project_id)

        # Create tasks for each selected user
        for user in selected_users:
            task = Task.objects.create(
                taskname=taskname,
                priority=priority,
                from_date=from_date,
                to_date=to_date,
                project=project,
                user=user,
                description=description,
                is_child=is_child,
                assigned_by=request.user
            )

            # Link parent task if "Is Child" is checked
            if is_child and parent_task_id:
                parent_task = Task.objects.get(id=parent_task_id)
                task.parent_task = parent_task
                task.save()

            # Create notification for each user
            Notification.objects.create(
                user=user,
                message=f"Task '{taskname}' created by {request.user.username}",
                assigned_by=request.user
            )

            # Send email notification to the user
            if user.email:  # Ensure the user has an email address
                subject = f"New Task Assigned: {taskname}"
                message = (
                    f"Dear {user.username},\n\n"
                    f"A new task has been assigned to you in the project '{project.projectname}'.\n"
                    f"Details:\n"
                    f"Task Name: {taskname}\n"
                    f"Priority: {priority}\n"
                    f"From Date: {from_date}\n"
                    f"To Date: {to_date}\n"
                    f"Description: {description}\n\n"
                    f"Please log in to the system to view more details.\n\n"
                    f"Best regards,\n"
                    f"{request.user.username}\n\n"
                    f"This is a system-generated email, please do not reply."
                )
                try:
                    send_mail(
                        subject,
                        message,
                        settings.EMAIL_HOST_USER,  # The sender's email address
                        [user.email],  # List of recipient email addresses
                        fail_silently=False,
                    )
                except Exception as e:
                    # Handle email sending errors
                    print(f"Failed to send email to {user.email}: {e}")

        # Redirect to the task details page
        return redirect('task_detail', project_id=project.id)



def mark_notifications_as_read(request):
    user = request.user
    if request.method == 'POST':  # Ensure it's a POST request
        # Mark all unread notifications for this user as read
        Notification.objects.filter(user=user, is_read=False).update(is_read=True)
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)  # Return an error for non-POST requests


def fetch_notifications(request):
    user = request.user  # Get the logged-in user
    notifications = Notification.objects.filter(user=user).order_by('-created_at')  # Fetch user's notifications
    kolkata_tz = pytz.timezone('Asia/Kolkata')  # Define Kolkata timezone

    notification_data = [{
        'assigned_by': notification.assigned_by.username,  # Show the username of the person who assigned the task
        'task_name': notification.message.split(" created the task ")[-1],  # Extract just the task name
        'created_at': notification.created_at.astimezone(kolkata_tz).strftime('%Y-%m-%d %I:%M %p')  # Format time in Kolkata timezone
    } for notification in notifications]

    # Fetch unread notifications for count
    unread_count = Notification.objects.filter(user=user, is_read=False).count()

    return JsonResponse({'notifications': notification_data, 'unread_count': unread_count})


@login_required
def delete_task(request, task_id):
    
    if request.method == 'POST':  # Only allow POST request for deletion
        try:
            # Get the task to delete
            task = get_object_or_404(Task, id=task_id)
            deleted_at = localtime()

            # Backup the task details before deleting
            DeletedTask.objects.create(
                taskname=task.taskname,
                priority=task.priority,
                from_date=task.from_date,
                to_date=task.to_date,
                user=task.user,
                project=task.project,
                deleted_at=deleted_at
            )

            # Delete the task from the Task table
            task.delete()

            # Return success response
            return JsonResponse({
                'status': 'success',
                'message': 'Task deleted successfully!',
                'deleted_at': deleted_at.strftime("%d-%m-%Y %H:%M:%S")
            }, status=200)

        except Exception as e:
            # Return error response if something goes wrong
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    # If the request method is not POST, return a bad request
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=400)



def specific_user_tasks_view(request, project_id):
    # Retrieve the project based on the project ID
    project = Project.objects.get(id=project_id)

    # Retrieve tasks for this project that are assigned to the logged-in user
    tasks = Task.objects.filter(project=project, user=request.user)

    # Add a property to child tasks indicating whether the parent task is completed
    processed_tasks = []
    for task in tasks:
        if task.is_child:
            if task.parent_task.status != 'Completed':
                task.is_faded = True  # Mark as faded
            else:
                task.is_faded = False  # No fade if parent is completed
        else:
            task.is_faded = False  # Regular tasks are not faded
        processed_tasks.append(task)

    context = {
        'project': project,
        'tasks': processed_tasks
    }

    return render(request, 'specific_user_task.html', context)


def specific_user_task_view_task_mgt(request, project_id, user_id):
    if request.method == 'POST':
        # Retrieve project and user objects
        project = get_object_or_404(Project, id=project_id)
        user = get_object_or_404(User, id=user_id)

        # Get form data
        taskname = request.POST.get('taskname')
        priority = request.POST.get('priority')
        from_date = request.POST.get('fromdate')
        to_date = request.POST.get('todate')
        description= request.POST.get('description')

        # Create a new task object
        task = Task(
            taskname=taskname,
            priority=priority,
            from_date=from_date,
            to_date=to_date,
            description=description,
            user=user,
            project=project
        )
        task.save()

        # Display success message and redirect to project page (or wherever you want)
        # messages.success(request, 'Task created successfully.')
        return redirect('specific_user_tasks_view', project_id=project.id)

    else:
        # If it's a GET request, render the form page
        return render(request, 'specific_user_task_form.html')
    


@csrf_exempt  # For handling AJAX request
def delete_task(request, task_id):
    if request.method == 'POST':
        task = get_object_or_404(Task, id=task_id)
        task.delete()
        return JsonResponse({'message': 'Task deleted successfully'}, status=200)
    else:
        return JsonResponse({'message': 'Invalid request method'}, status=400)
    
def update_task(request, task_id):
    if request.method == 'POST':
        task = get_object_or_404(Task, id=task_id)
        task.taskname = request.POST.get('taskname')
        task.description = request.POST.get('description')  # Update description
        task.priority = request.POST.get('priority')
        task.from_date = request.POST.get('fromdate')
        task.to_date = request.POST.get('todate')
        task.save()

        return JsonResponse({'status': 'success'})  # Return success response

    return JsonResponse({'status': 'error'}, status=400)  # Handle GET requests or invalid methods

    # return redirect('task_detail', project_id=task.project.id)  # Fallback redirect

def edit_projects(request, project_id):
    project = get_object_or_404(Project, id=project_id)  # Get the project by ID
    if request.method == 'POST':
        # Get the updated values from the form
        project.projectname = request.POST.get('projectname')
        project.priority = request.POST.get('priority')
        project.from_date = request.POST.get('fromdate')
        project.to_date = request.POST.get('todate')

        # Save the updated project details
        project.save()

        # Redirect to a project list or a specific project page
        return redirect('user_project', user_id=project.user.id)  # Assuming project has a related 'user' field

    return HttpResponse("Invalid request method", status=400)


def allprojects(req):
    print("hello")
    # Get the current user's groups
    user_groups = req.user.groups.values_list('name', flat=True)

    # Exclude projects for 'superadmin' and 'normaluser' groups
    if 'superadmin' in user_groups:
        print("all")
        # Show all projects or projects specific to superadmin
        projects = Project.objects.all()  # Adjust based on your logic
    elif 'normaluser' in user_groups:
        # Exclude normal user projects (you can adjust the filter based on the logic you need)
        projects = Project.objects.exclude(user_groups_name='normaluser')
    else:
        # If the user belongs to any other group, fetch all their assigned projects
        projects = Project.objects.filter(user=req.user)

    return render(req, "allprojects.html", {'projects': projects})



        
from django.shortcuts import render
from django.contrib.auth.models import Group
from .models import Project

def all_projectss(request):
    # Get the Superadmin group
    superadmin_group = Group.objects.get(name='Superadmin')

    # Exclude projects where the user belongs to the Superadmin group
    projects = Project.objects.exclude(user__groups=superadmin_group).order_by('-created_at')

    context = {
        'projects': projects
    }
    return render(request, 'all_projects1.html', context)


def all_projects_with_tasks(request):
    print("Fetching tasks for the user")

    if request.user.is_authenticated:
        # Fetch all projects (common to all users)
        projects = Project.objects.all().order_by('-created_at')

        user_tasks = []  # To store tasks assigned to the logged-in user
        selected_status = request.POST.get('status') if request.method == 'POST' else None

        # Iterate over each project to get tasks specific to the logged-in user
        for project in projects:
            # Filter tasks for the logged-in user
            tasks = project.tasks.filter(user=request.user)
            if selected_status:  # Apply status filter if provided
                tasks = tasks.filter(status=selected_status)

            # Filter out child tasks if their parent is not completed
            filtered_tasks = []
            for task in tasks:
                if not task.is_child:  # If the task is not a child, add it
                    filtered_tasks.append({
                        'task': task,
                        'disabled': False  # Not disabled
                    })
                elif task.is_child:
                    # If the parent task is not completed, mark it as disabled
                    disabled = task.parent_task.status != 'Completed'
                    filtered_tasks.append({
                        'task': task,
                        'disabled': disabled  # Mark child task as disabled based on parent's status
                    })

            if filtered_tasks:  # Add only if there are tasks to display after filtering
                user_tasks.append({
                    'project': project,
                    'tasks': filtered_tasks
                })
            print(f"Tasks for {project.projectname} assigned to {request.user.username}: {filtered_tasks}")

        # Pass the user's tasks and projects to the template
        context = {
            'user_tasks': user_tasks,  # This will hold projects with tasks specific to the user
            'selected_status': selected_status, 
        }
        print("Rendering HTML with user-specific tasks")
        return render(request, 'all_projects_with_tasks.html', context)

    else:
        # Redirect to login page if not authenticated
        return redirect('login')



# def filtertask_list(request):
#     # Get the selected status from the GET request
#     if request.method =='POST':

#         selected_status = request.POST.get('status')
#         print(selected_status,"ll")

#         # Filter tasks based on the selected status
#         if selected_status:
#             tasks = Task.objects.filter(status=selected_status)
#             print(tasks,"select task")
#         else:
#             tasks = Task.objects.all()

#         context = {
#             'tasks': tasks,
#             'selected_status': selected_status,  # Pass the selected status for template use
#         }
#         return render(request, 'all_projects_with_tasks.html', context)





from django.contrib.auth.models import Group

def all_users_tasks(request):
    if request.user.is_authenticated:
        # Check if the user is either a Superadmin or Admin
        if request.user.groups.filter(name__in=['Superadmin', 'Admin']).exists():
            # Fetch projects excluding the current user's own projects
            projects = Project.objects.exclude(user=request.user).order_by('-created_at')

            # Check if the logged-in user is an Admin (but not a Superadmin)
            if request.user.groups.filter(name='Admin').exists():
                # Fetch tasks excluding those related to Superadmin users
                superadmin_group = Group.objects.get(name='Superadmin')
                superadmin_users = superadmin_group.user_set.all()

                # Exclude tasks from projects created by Superadmin users
                tasks = Task.objects.filter(project__in=projects).exclude(project__user__in=superadmin_users).order_by('-from_date')
            else:
                # If the logged-in user is a Superadmin, show all tasks
                tasks = Task.objects.filter(project__in=projects).order_by('-from_date')
             # Apply status filter if selected
            selected_status = request.POST.get('status', None)
            if selected_status:
                tasks = tasks.filter(status=selected_status)
            
            context = {
                'projects': projects,
                'tasks': tasks,  # Pass the filtered tasks to the template
                'selected_status': selected_status,
            }

            return render(request, 'allusertasks.html', context)
        else:
            return render(request, 'unauthorized.html')  
    else:
        return redirect('login')





@csrf_exempt
def mark_comments_as_read(request, task_id):
    if request.method == 'POST':
        # Update comments for the task and mark them as read
        comments = Comment.objects.filter(task_id=task_id, user__groups__name='Superadmin', read=False)
        comments.update(read=True)

        return JsonResponse({'success': True})
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})

# -=--------------------------------------------------------------------------------------------------

def todo_card_detail_view(request, task_id):
    task = get_object_or_404(Task, id=task_id)  # Get the task by ID
    todolist_entries = Todolist.objects.filter(task=task)  # Filter to-dos by task

    task_counts = {
        'todo': todolist_entries.filter(status='todo').count(),
        'in_progress': todolist_entries.filter(status='in_progress').count(),
        'done': todolist_entries.filter(status='done').count(),
    }

    context = {
        'task': task,
        'task_counts': task_counts,
        'todolist_entries': todolist_entries  # Filtered to-dos for this task
    }

    return render(request, 'usercard.html', context)



def kanban_view(request):
    if request.user.is_authenticated:
        # Fetch tasks for the logged-in user
        tasks = Task.objects.filter(project__user=request.user).order_by('-from_date')

        context = {
            'tasks': tasks,  # Pass the tasks to the template
        }
        return render(request, 'usercard.html', context)
    else:
        return redirect('login')
    

   
def edit_task(request):
    if request.method == 'POST':
        task_id = request.POST.get('task_id')
        task_name = request.POST.get('taskname')
        task_status = request.POST.get('status')

        # Get the task object and update it with the new data
        task = get_object_or_404(Task, id=task_id)
        task.taskname = task_name
        task.status = task_status
        task.save()

        return redirect('kanban_view')  # Redirect to the Kanban view after updating

    return redirect('kanban_view')

    

@login_required
def get_tasks_for_kanban_view(request):
    user = request.user
    
    # Filter tasks based on the logged-in user and their statuses
    todo_tasks = Task.objects.filter(user=user, status='Not Started')
    in_progress_tasks = Task.objects.filter(user=user, status='Working')
    completed_tasks = Task.objects.filter(user=user, status='Completed')
    pending_review_tasks = Task.objects.filter(user=user, status='Pending Review')
    cancelled_tasks = Task.objects.filter(user=user, status='Cancelled')
    rework_tasks = Task.objects.filter(user=user, status='Rework')  # New line for Rework tasks

    # Filtering child tasks based on parent status
    def filter_child_tasks(tasks):
        filtered_tasks = []
        for task in tasks:
            if not task.is_child:
                filtered_tasks.append(task)
            elif task.is_child and task.parent_task.status == 'Completed':
                filtered_tasks.append(task)
        return filtered_tasks

    todo_tasks_custom = filter_child_tasks(todo_tasks)
    in_progress_tasks_custom = filter_child_tasks(in_progress_tasks)
    completed_tasks_custom = filter_child_tasks(completed_tasks)
    pending_review_tasks_custom = filter_child_tasks(pending_review_tasks)
    cancelled_tasks_custom = filter_child_tasks(cancelled_tasks)
    rework_tasks_custom = filter_child_tasks(rework_tasks)  # Filtering Rework tasks

    context = {
        'todo_tasks_custom': todo_tasks_custom,
        'in_progress_tasks_custom': in_progress_tasks_custom,
        'completed_tasks_custom': completed_tasks_custom,
        'pending_review_tasks_custom': pending_review_tasks_custom,
        'cancelled_tasks_custom': cancelled_tasks_custom,
        'rework_tasks_custom': rework_tasks_custom,  # Adding to context
    }
    
    return render(request, 'usercard.html', context)


@csrf_exempt
def get_comments(request, task_id):
    comments = Comment.objects.filter(task_id=task_id).values('text', 'comment_timestamp', 'user__username')

    comments_list = [
        {
            'text': comment['text'],
            'timestamp': timezone.localtime(comment['comment_timestamp']).strftime('%Y-%m-%d %H:%M:%S'),
            'username': comment['user__username']  # Include the username
        }
        for comment in comments
    ]

    return JsonResponse({'success': True, 'comments': comments_list})


@csrf_exempt
def add_comment(request, task_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        comment_text = data.get('comment')

        task = Task.objects.get(id=task_id)

        # Get the logged-in user
        user = request.user

        # Create the new comment and associate it with the user
        new_comment = Comment.objects.create(task=task, text=comment_text, user=user)

        return JsonResponse({
            'success': True,
            'comment': new_comment.text, 
            'timestamp': new_comment.comment_timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'username': new_comment.user.username  # Return username
        })
    return JsonResponse({'success': False, 'message': 'Invalid request'})

@csrf_exempt
def update_task_status_cards_drag(request, task_id):
    if request.method == 'POST':
        try:
            # Parse the request body to get the new status
            data = json.loads(request.body)
            new_status = data.get('status')

            # Fetch the task using the Task model
            task = Task.objects.get(id=task_id)
            
            # Update the task's status and save it to the database
            task.status = new_status
            task.save()

            # Return a success response
            return JsonResponse({'success': True})

        except Task.DoesNotExist:
            return JsonResponse({'error': 'Task not found'}, status=404)
        
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    # Return an error response if the request method is not POST
    return JsonResponse({'error': 'Invalid request method'}, status=400)



def userprofile(req):
    # Retrieve or create the user profile
    user_profile, created = UserProfile.objects.get_or_create(user=req.user)

    if req.method == 'POST':
        print("Image upload initiated")
        # Handle the image upload or other POST actions here
        return render(req, "user_profile.html", {"user_profile": user_profile})

    # For GET requests, render the user profile page
    return render(req, "user_profile.html", {"user_profile": user_profile})



@login_required
def upload_profile_image(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST' and 'image' in request.FILES:
        image = request.FILES['image']
        extension = os.path.splitext(image.name)[1].lower()
        allowed_extensions = ['.jpg', '.jpeg', '.png']

        # Check if the file extension is allowed
        if extension not in allowed_extensions:
            return JsonResponse({
                'status': 'error',
                'message': "Only JPG, JPEG, and PNG files are allowed."
            })

        user_profile.image = image
        user_profile.save()
        # return JsonResponse({'status': 'success', 'message': 'Image uploaded successfully!'})

    return redirect("userprofile")


@login_required
def delete_profile_image(request):
    print("Delete request received")
    if request.method == 'POST':
        user_profile = UserProfile.objects.get(user=request.user)
        user_profile.image.delete(save=False)
        user_profile.image = None
        user_profile.save()
        return redirect('userprofile')
    
