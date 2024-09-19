from django.urls import path
from . import views

urlpatterns = [
    path('members/', views.members, name='members'),
    # path('', views.login, name='login'),
    path('forms/', views.forms, name='forms'),
    path('tables/', views.tables, name='tables'),
    path('chartaccount/', views.chartaccount, name='chartaccount'),
    path('assets/', views.assets, name='assets'),
    path('currentassets/', views.currentassets, name='currentassets'),
    path('fdwithbank/', views.fdwithbank, name='fdwithbank'),
    path('custom_admin/', views.custom_admin, name='custom_admin'),    
    path('todolist/', views.todolist, name='todolist'),     
    path('components/', views.components, name='components'),
    path('todlistpage/', views.todlistpage, name='todlistpage'),

    path('todopgt/', views.todopgt, name='todopgt'),    
    path('projects/<int:project_id>/', views.projects, name='projects'),
    path('projects/<int:project_id>/create_issue/', views.create_issue, name='create_issue'),
    # path('issue/edit/<int:issue_id>/', views.edit_issue, name='edit_issue'),

    path('issue/delete/<int:issue_id>/', views.delete_issue, name='delete_issue'),
    path('delete_project/<int:project_id>/', views.delete_project, name='delete_project'),

    path('register/', views.register, name='register'),  # URL for the register page
    path('', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),  # URL for the logout view
    path('projects/<int:project_id>/create-todolist/', views.create_todolist, name='create_todolist'),
    path('api/projects/all/', views.fetch_all_data, name='fetch_all_data'),
    path('user_list/', views.user_list, name='user_list'), 
    path('delete_user/<int:user_id>/', views.delete_user, name='delete_user'),
    path('user-project/<int:user_id>/', views.user_project, name='user_project'),
    path('create_user/', views.create_user, name='create_user'),
    path('user-project/<int:user_id>/create/', views.create_project, name='create_project'),
    path('project/edit/<int:project_id>/', views.edit_project, name='edit_project'),
    path('project/delete/<int:project_id>/', views.delete_project, name='delete_project'),
    path('tasks/', views.task_view, name='task_view'),  # URL to render the tasks view

    path('update-task-status/', views.update_task_status, name='update_task_status'),
    path('assigned_projects_view/', views.assigned_projects_view, name='assigned_projects_view'),
    path('update_status/<int:project_id>/', views.update_status, name='update_status'),
    # 1111
    path('project/<int:project_id>/', views.project_detail, name='project_detail'),  # New route for project detail
    
    path('project/<int:project_id>/create_task/', views.create_task, name='create_task'),
    path('delete_task/<int:task_id>/', views.delete_task, name='delete_task'),
    path('specific_user_tasks_view/<int:project_id>/', views.specific_user_tasks_view, name='specific_user_tasks_view'),
   
    path('specificprojectstask/<int:project_id>/users/<int:user_id>/tasks/add/', views.specific_user_task_view_task_mgt, name='specificusertask'),
    path('delete_task/<int:task_id>/', views.delete_task, name='delete_task'),
    path('update-task/<int:task_id>/', views.update_task, name='update_task'),
    path('project/edit/<int:project_id>/', views.edit_projects, name='edit_project'),

    # path('project/<int:project_id>/tasks/', views.project_tasks, name='project_tasks'),
    # path('add_comment/', views.add_comment, name='add_comment'),







    




    





    

    




    

    


    

    

    

    

    



]