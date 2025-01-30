from django.urls import path
from . import views
# from .views import UserListView

urlpatterns = [
    path('', views.user_login, name='login'),
    path('members/', views.members, name='members'),
    path('tables/', views.tables, name='tables'),
    path('custom_admin/', views.custom_admin, name='custom_admin'),    
    path('todlistpage/', views.todlistpage, name='todlistpage'),
    path('components/', views.components, name='components'),
    path('save-logout-time/', views.save_logout_time, name='save_logout_time'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('group/<str:group_name>/', views.allusersview, name='group_users'),
    path('tasks/<int:user_id>/', views.tasks_view, name='tasks_view'),
    path('tasks/filter/<int:user_id>/<str:status>/', views.dashboardtaskview, name='filter_tasks'),
    path('todopgt/', views.todopgt, name='todopgt'),    
    path('projects/<int:project_id>/', views.projects, name='projects'),
    path('todotable/', views.todotable, name='todotable'),
    path('project/delete/<int:project_id>/', views.delete_project, name='delete_project'),
    path('register/', views.register, name='register'),  
    path('loginerror/', views.loginerror, name='loginerror'),
    path('logout/', views.user_logout, name='logout'), 
    path('todolist/create/<int:task_id>/', views.create_todolist, name='create_todolist'),
    path('api/projects/all/', views.fetch_all_data, name='fetch_all_data'),
    path('user_list/', views.user_list, name='user_list'),
    path('delete_user/<int:user_id>/', views.delete_user, name='delete_user'),
    path('export/completed-tasks/', views.export_ontime_completed_tasks, name='export_ontime_completed_tasks'),
    path('export/overdue-completed-tasks/', views.export_overdue_completed_tasks, name='export_overduecompleted_tasks'),
    path('export/total-completed-tasks/', views.export_total_completed_tasks, name='export_total_completed_tasks'),

    path('user-project/', views.user_project, name='user_project'),
    path('create_user/', views.create_user, name='create_user'),
    path('user-project/create/', views.create_project, name='create_project'),
    path('project/edit/<int:project_id>/', views.edit_project, name='edit_project'),
    path('project/delete/<int:project_id>/', views.delete_project, name='delete_project'),
    path('tasks/', views.task_view, name='task_view'),  
    path('todo_card_detail_view/<int:task_id>/', views.todo_card_detail_view, name='todo_card_detail_view'),
    path('update-task-status/<int:task_id>/', views.update_task_status, name='update_task_status'),
    path('assigned_projects_view/', views.assigned_projects_view, name='assigned_projects_view'),
    path('update_status/<int:project_id>/', views.update_status, name='update_status'),
    path('project/<int:project_id>/', views.task_detail, name='project_detail'), 
    path('create-task/<int:project_id>/', views.create_task, name='create_task'), 
    path('specific_user_tasks_view/<int:project_id>/', views.specific_user_tasks_view, name='specific_user_tasks_view'),
    path('specificprojectstask/<int:project_id>/users/<int:user_id>/tasks/add/', views.specific_user_task_view_task_mgt, name='specificusertask'),
    path('delete_task/<int:task_id>/', views.delete_task, name='delete_task'),
    path('task/update/<int:task_id>/', views.update_task, name='update_task'),
    path('project/edit/<int:project_id>/', views.edit_project, name='edit_project'),
    path('allprojects/', views.allprojects, name='allprojects'),
    path('all_projectss/', views.all_projectss, name='all_projectss'),
    path('all_projects_with_tasks/', views.all_projects_with_tasks, name='all_projects_with_tasks'),
    path('all_users_tasks/', views.all_users_tasks, name='all_users_tasks'),
    path('card_update_task_status/<int:task_id>/', views.card_update_task_status, name='card_update_task_status'),
    path('add-comment/<int:task_id>/', views.add_comment, name='add_comment'),
    path('get-comments/<int:task_id>/', views.get_comments, name='get_comments'),
    path('kanban-view/', views.get_tasks_for_kanban_view, name='kanban_view'),
    path('edit-task/', views.edit_task, name='edit_task'),
    path('mark-comments-as-read/<int:task_id>/', views.mark_comments_as_read, name='mark_comments_as_read'),
    path('update-task-status/<int:task_id>/', views.update_task_status_cards_drag, name='update_task_status'),
    
    path('projects/<int:project_id>/tasks/', views.task_detail, name='task_detail'), 
    path('fetch-notifications/', views.fetch_notifications, name='fetch_notifications'),
    path('mark-notifications-read/', views.mark_notifications_as_read, name='mark-notifications-read'),
    path('userprofile/', views.userprofile, name='userprofile'),
    path('profile/upload-image/', views.upload_profile_image, name='upload_profile_image'),
    path('profile/delete-image/', views.delete_profile_image, name='delete_profile_image'),
    path('get-user-login-history/', views.get_user_login_history, name='get_user_login_history'),
    path('loginusers/', views.loginusers, name='loginusers'),
    path('filter-login-history-by-date/', views.filter_login_history_by_date, name='filter_login_history_by_date'),  
    path('export-superadmins/', views.export_superadmins, name='export_superadmins'),
    path('export-admins/', views.export_admins, name='export_admins'),
    path('export-users/', views.export_users, name='export_user'),
    path('export-tasks/', views.export_user_tasks, name='export_user_tasks'),
    path('export-not-started-tasks/', views.export_not_started_tasks, name='export_not_started_tasks'),
    path('export_working_tasks/', views.export_working_tasks, name='export_working_tasks'),
    path('export_completed_tasks/', views.export_completed_tasks, name='export_completed_tasks'),
    path('export_rework_tasks/', views.export_rework_tasks, name='export_rework_tasks'),
    path('export_pending_review_tasks/', views.export_pending_review_tasks, name='export_pending_review_tasks'),
    path('export_cancelled_tasks/', views.export_cancelled_tasks, name='export_cancelled_tasks'),
    path('export-user-tasks/', views.export_user_tasks, name='export_user_tasks'),
    ]


    

    

    



