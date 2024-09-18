from django.shortcuts import render,redirect,get_object_or_404
from .models import *
from django.views.decorators.http import require_POST
from django.contrib.auth.models import User
from django.contrib.auth import login as auth_login, authenticate ,logout as auth_logout # Import login and rename it to auth_login
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.urls import reverse
import re
from django.utils.timesince import timesince
from django.http import JsonResponse,HttpResponse
from django.utils.dateformat import format
from django.db.models import Max
from django.utils.timezone import localtime
from django.utils import timezone


def createuserpage(req):
    return render(req,"createuserpage.html")


def create_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        
        # Create the user
        User.objects.create_user(username=username, email=email, password=password)
        print("user saved")

        
        
        # Redirect to the admin interface
        return redirect('admin:index')  # Redirects to the Django admin home

    return render(request, 'create_user.html')

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        mobile = request.POST['mobile']

        password = request.POST['password']
        password2 = request.POST['cpassword']

        
         # Initialize the response dictionary
        response = {'status': 'success'}

            # Email validation regex to check format
        if not re.match(r'^[a-zA-Z0-9._%+-]+@gmail\.com$', email):
            response = {'status': 'error', 'message': 'Invalid email format. Email must end with @gmail.com'}
            return JsonResponse(response)
        
          # Check if mobile already exists
        if UserProfile.objects.filter(mobile=mobile).exists():
            response = {'status': 'error', 'message': 'Mobile number already in use'}
            return JsonResponse(response)
        

        # Check if mobile number is valid (e.g., length and numeric)
        if not re.match(r'^\d{10}$', mobile):
            response = {'status': 'error', 'message': 'Invalid mobile number. Must be 10 digits.'}
            return JsonResponse(response)



        # Check if passwords match
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

        # Check if email already exists
        if User.objects.filter(email=email).exists():
            response = {'status': 'error', 'message': 'Email already in use'}
            return JsonResponse(response)


        # Create the user
        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()


        # Create user profile with mobile number
        user_profile = UserProfile.objects.create(user=user, mobile=mobile)
        user_profile.save()


         # Log the user out to ensure no session persists after registration
        auth_logout(request)


        # Return JSON response with success status and the login URL
        response = {
            'status': 'success',
            'message': 'Registration successful!',
            'redirect_url': reverse('login')  # Pass the login URL
        }

        return JsonResponse(response)

    return render(request, 'register.html')


    



def user_login(request):
    # Check if the user is already authenticated
    if request.user.is_authenticated:
        return redirect('members')  # Redirect to members page if user is logged in

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
            return JsonResponse({'status': 'success', 'redirect_url': reverse('todlistpage')})
        else:
            # Return an error response if the password is incorrect
            return JsonResponse({'status': 'error', 'message': 'Invalid login credentials'})
    
    return render(request, 'login.html')




@login_required
def members(request):
    print("member fun")

 
    if request.user.is_authenticated:
        print("f true")
        username = request.user.username
        return render(request, 'all_leads.html', {'username': username})
    else:
        print("if fail")
        return redirect('login')


def user_logout(request):
   if request.method == 'POST':  # Only allow logout on POST request
        auth_logout(request)
        return redirect('login')  # Redirect to login after logout
   return redirect('members')  # If not logged out, redirect to members



# def forgotpassword(request):
#     return render(request,"forgotpassword.html")




def forms(request):
    return render(request,"forms.html")

@login_required
def tables(request):
    return render(request,"tables-data.html")

def chartaccount(req):
    return render(req,"ca_accounts.html")


def assets(req):
    return render(req,"assets.html")


def currentassets(req):
    return render(req,"currentassets.html")



def fdwithbank(req):
    return render(req,"fdwithbank.html")




def todolist(request):
    print("todo")
    return render(request,"todolist.html")



def custom_admin(request):
    return render(request,"custom_admin.html")




def components(request):
    return render(request,"components.html")


def todlistpage(request):
    print("tolistpage fun")
    # Retrieve all projects, ordered by creation time (most recent first)
    projects = Project.objects.filter(user=request.user).order_by('-created_at')
    status_choices = Project.STATUS_CHOICES

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
        print(projectname)
        if projectname:
            print("pgt if")
            # Create and save the project
            Project.objects.create(
                projectname=projectname,
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

def delete_project(request, project_id):
    print("Arun pgt function")
    project = get_object_or_404(Project, id=project_id)
    
    deleted_at_utc = timezone.now()  # Get the current time in UTC
    deleted_at_local = timezone.localtime(deleted_at_utc)


    archived_project = ArchivedProject(
        projectname=project.projectname,
        taskname=project.taskname,
        priority=project.priority,
        from_date=project.from_date,
        to_date=project.to_date,
        created_at=project.created_at,
        updated_at=project.updated_at,
        deleted_at=deleted_at_local,  # Set the deletion date and time
  # Set the deletion date and time

        user=project.user,
        assigned_by=project.assigned_by,
        status=project.status,
    )
    archived_project.save()
    print(f"Project {project_id} deleted at {deleted_at_local.strftime('%Y-%m-%d %H:%M:%S')}")
    print("Deleted Projet Saved")

    # Delete the original project
    project.delete()
    
    return redirect('todlistpage')

def create_issue(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    
    if request.method == 'POST':
        issuename = request.POST.get('issuename')
        print(issuename)
        if issuename:
            print("if",issuename)
            Issue.objects.create(project=project, title=issuename, description=issuename)
            return redirect('projects', project_id=project.id)
    
    return render(request, 'todolist.html', {'project': project})




def edit_issue(request, issue_id):
    issue = get_object_or_404(Issue, id=issue_id)
    
    if request.method == 'POST':
        issue.description = request.POST.get('description')
        issue.save()
        
        return redirect('projects', project_id=issue.project.id)  # Redirect to the project's issues view

    return render(request, 'edit_issue.html', {'issue': issue})


@require_POST
def delete_issue(request, issue_id):
    print("print delete issue")
    issue = get_object_or_404(Issue, id=issue_id)
    project_id = issue.project.id  # Capture the project ID before deleting
    issue.delete()
    return redirect('projects', project_id=project_id)  # Redirect to the projects view after deletion


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
    print("Fetching all comments")

    # Fetch all comments from the Todolist model
    todotasks = Todolist.objects.all()

    # Serialize only the comment data
    data = []
    for task in todotasks:
        data.append({
            'id': task.id,
            'comment': task.comments,  # Fetching the comments
            'created_at': task.created_at.isoformat(),  # Ensure ISO 8601 format

        })

    return JsonResponse(data, safe=False)


@login_required
def user_list(request):
    if request.user.groups.filter(name__in=["Admin", "SuperAdmin"]).exists():
            users = User.objects.exclude(is_superuser=True).exclude(id=request.user.id)
            return render(request, 'user_list.html', {'users': users})
    else:
        # Redirect non-superusers or show a permission denied message
            return JsonResponse({'error': 'Permission Denied'}, status=403)
    

@login_required
def delete_user(request, user_id):
    if request.user.is_superuser:
        user = get_object_or_404(User, id=user_id)
        
        # Archive the user details before deletion
        ArchivedUser.objects.create(
            username=user.username,
            email=user.email,
            date_joined=user.date_joined
        )
        
        # Delete the user
        user.delete()
        
        return JsonResponse({'success': 'User deleted successfully.'})
    else:
        return JsonResponse({'error': 'Permission Denied'}, status=403)


def create_project(request, user_id):
    print("create pgt function")
    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        # Get form data from POST request
        projectname = request.POST.get('projectname')
        # taskname = request.POST.get('taskname')
        priority = request.POST.get('priority')
        from_date = request.POST.get('fromdate')
        to_date = request.POST.get('todate')

        try:
            print("try block")
            # Create and save new Project instance, linking it to the user
            project = Project(
                projectname=projectname,
                # taskname=taskname,
                priority=priority,
                from_date=from_date,
                to_date=to_date,
                user=user,  # Associate the project with the selected user
                assigned_by=request.user  # Set the user creating the project

            )
            project.save()
            print(" project data saved")

            # Redirect back to the user's project page
            return redirect('user_project', user_id=user.id)

        except Exception as e:
            print("except")
            return HttpResponse(f"An error occurred: {e}", status=500)

    # If GET request, just render the page with the user's existing projects
    projects = Project.objects.filter(user=user)
    return render(request, 'userproject.html', {'projects': projects, 'user': user})


def user_project(request, user_id):
    print("user_project function")
    # Get the user by ID or return 404 if not found
    user = get_object_or_404(User, id=user_id)

    # Get all projects associated with the specific user
    user_projects = Project.objects.filter(user=user).order_by('-created_at')
    print("this is the user_projects",user_projects)
    context = {
        'user': user,  # Pass the selected user
        'projects': user_projects,  # Pass the projects for this user
    }

    return render(request, 'userproject.html', context)






def edit_project(request, project_id):
    print("edit pgt")
    project = get_object_or_404(Project, id=project_id)
    
    if request.method == 'POST':
        if request.user.is_superuser:
            project.projectname = request.POST.get('projectname')
            # project.priority = request.POST.get('priority')
            project.from_date = request.POST.get('fromdate')
            # print(project.taskname)
            # project.to_date = request.POST.get('todate')
        else:

        

            project.projectname = request.POST.get('projectname')
            project.taskname = request.POST.get('taskname')
            project.priority = request.POST.get('priority')
            project.from_date = request.POST.get('fromdate')
            project.to_date = request.POST.get('todate')
        
        project.save()
        if request.user.is_superuser:
            return redirect("todlistpage")
        else:
            return redirect('user_project', user_id=project.user.id)




    
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

def update_task_status(request):
    if request.method == 'POST':
        task_id = request.POST.get('task_id')
        new_status = request.POST.get('status')

        # Retrieve the task or return error if not found
        task = get_object_or_404(Todolist, id=task_id)

        # Update the task status
        task.status = new_status
        task.save()

        # Respond with a success status
        return JsonResponse({'status': 'success'})

    return JsonResponse({'status': 'error', 'message': 'Invalid request'})


def task_view(request):
    todotasks = Todolist.objects.filter(status='todo')
    in_progress_tasks = Todolist.objects.filter(status='in_progress')
    done = Todolist.objects.filter(status='done')

    context = {
        'todotask': todotasks,
        'in_progress_tasks': in_progress_tasks,
    }

    return render(request, 'todolist.html', context)


def project_detail(request, project_id):
    print("vinpoth")
    # Get the project by ID or return 404 if not found
    project = get_object_or_404(Project, id=project_id)

    # Get all tasks for the selected project
    project_tasks = Task.objects.filter(project=project).order_by('-from_date')
    
    # Get all projects for the same user (for retaining the full table if needed)
    user_projects = Project.objects.filter(user=project.user).order_by('-created_at')
    
    context = {
        'selected_project': project,  # Pass the selected project
        'projects': user_projects,    # Pass all projects for the user
        'tasks': project_tasks,       # Pass the tasks related to the selected project
    }

    return render(request, 'task_detail.html', context)



def create_task(request, project_id):
    if request.method == "POST":
        # Get the related project by ID
        project = get_object_or_404(Project, id=project_id)

        # Extract form data
        taskname = request.POST.get('taskname')
        priority = request.POST.get('priority')
        fromdate = request.POST.get('fromdate')
        todate = request.POST.get('todate')

        # Validate the data and create the task object
        if taskname and priority and fromdate and todate:
            # Create a new task and associate it with the specific project
            task = Task.objects.create(
                project=project,
                user=request.user,  # Assign the current logged-in user to the task

                taskname=taskname,
                priority=priority,
                from_date=fromdate,
                to_date=todate,
            )
            task.save()

            # Success message

            # Redirect to the project detail page after saving the task
            return redirect('project_detail', project_id=project.id)
        else:
            # Error message if fields are not filled
            # messages.error(request, 'Please fill all the fields.')

            # Reload the form with the selected project
            return redirect('project_detail', project_id=project.id)

    # In case of GET request, redirect to project detail page
    return redirect('project_detail', project_id=project_id)



@login_required
def delete_task(request, task_id):
    # Get the task to delete
    task = get_object_or_404(Task, id=task_id)
    deleted_at = localtime(timezone.now())


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

    # Now delete the task from the Task table
    task.delete()
    deletion_time_formatted = deleted_at.strftime("%d-%m-%Y %H:%M:%S")
    print(deletion_time_formatted,"Deleted time and date")


    # Success message
    # messages.success(request, "Task deleted successfully!")

    # Redirect to the project detail page or task list
    return redirect('project_detail', project_id=task.project.id)


def specific_user_tasks_view(request, project_id):
    # Get the project by its ID
    project = get_object_or_404(Project, id=project_id)
    
    # Get the tasks related to the project
    tasks = Task.objects.filter(project=project)

    context = {
        'project': project,
        'tasks': tasks,
    }
    
    return render(request, 'specific_user_task.html', context)

# @login_required
# def task_detail_view(request, project_id):
#     project = get_object_or_404(Project, id=project_id)
#     tasks = Task.objects.filter(project=project)
#     context = {
#         'project': project,
#         'tasks': tasks,
#     }
#     return render(request, 'task_detail.html', context)


# @login_required
# def add_comment(request):
#     print("cmd section")
#     if request.method == 'POST':
#         project_id = request.POST.get('project_id')
#         comment_text = request.POST.get('comment')

#         if project_id and comment_text:
#             project = Project.objects.get(id=project_id)
#             Comment.objects.create(
#                 user=request.user,
#                 project=project,
#                 text=comment_text
#             )
#             return redirect(reverse('project_tasks', kwargs={'project_id': project_id}))

#     return redirect('/')
