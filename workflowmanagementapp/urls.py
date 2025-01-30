from django.urls import path
from . import views
from .views import *


urlpatterns = [

    path('mailtemplate/', views.mailtemplate, name='mailtemplate'),
    path('send/<int:recipient_id>/', views.send_message, name='send_message'),  
    path('group/<int:group_id>/send_message/', views.send_group_message, name='send_group_message'),
    path('group/<int:group_id>/', views.group_detail, name='group_detail'),
    path('msg/', views.msg, name='msg'),
    path('sms/', views.sms, name='sms'),
    path('search/', views.search_users, name='search_users'),
    path('get-notifications/', views.get_notifications, name='get_notifications'),
    path('mark-message-as-read/', views.mark_message_as_read, name='mark_message_as_read'),
    # path('sms/<int:user_id>/', views.sms, name='sms'),

    path('mark-notifications-as-read/', views.mark_notifications_as_read, name='mark_notifications_as_read'),
    path('delete-message/<int:message_id>/', views.delete_message, name='delete_message'),
    path('create_group/', views.create_group, name='create_group'),
    path('check-message-status/', views.check_message_status, name='check-message-status'),
    path('create_group/', views.create_group, name='create_group'),
    path('workflowmgt', views.workflowmgt, name='workflowmgt'),  
    path('leave/', LeaveRequestView.as_view(), name='leave_request'),
    path('leave/<int:leave_id>/approve/', views.approve_leave, name='approve_leave'),
    path('leave/<int:leave_id>/reject/', views.reject_leave, name='reject_leave'),
    path('withdraw_leave/<int:leave_id>/', WithdrawLeaveView.as_view(), name='withdraw_leave'),
    path('gst1/', views.gst1, name='gst1'),  
    path('download-sample-book/', views.download_sample_book, name='download_sample_book'),
    path('download_sample_portal/', views.download_sample_portal, name='download_sample_portal'),
    path('mailtemp/', mailtemp, name='mailtemp'),
    path('get_stored_emails/', views.get_stored_emails, name='get_stored_emails'),
    path('maill/', views.maill, name='maill'),

    path('meeting/', views.meeting, name='meeting'),
    path('meetingsave/', views.meetingsave, name='meetingsave'),
    path('meeting_list/', views.meeting_list,name='meeting_list'),
    path('meetingsend/<int:id>/', views.meetingsend, name='meetingsend'),
    path('after_meeting/<int:id>/', views.after_meeting, name='after_meeting'),
    path('delete_meeting/<int:id>/', views.delete_meeting, name='delete_meeting'),
    path('points_discussed/<int:id>/', views.points_discussed, name='points_discussed'),
    path('assign_tasks/<int:id>/', views.points_agreed, name='points_agreed'),
    path('minutes/<int:id>/', views.minutes_of_meeting, name='minutes_of_meeting'),
    path('send_mom/<int:id>/', views.send_mom, name='send_mom'),







]
