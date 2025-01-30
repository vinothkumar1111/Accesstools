from django.contrib import admin
from .models import *
from workflowmanagementapp.models import *
from django.contrib.admin.models import LogEntry

class GroupRestrictedAdmin(admin.ModelAdmin):
    """
    Restrict table visibility based on user group.
    - Superadmin can view all models.
    - Admin can only view the Group model.
    - Other users can't view any models.
    """

    def has_module_permission(self, request):
        # Superadmin can view all models
        if request.user.groups.filter(name='Superadmin').exists():
            return True
        
        # Admin can only view the 'Group' model
        if request.user.groups.filter(name='Admin').exists():
            # Restrict access to other models, only show Group model
            if self.model == Group:
                return True
            return False
        
        # Other users can't view any models
        return False

    def has_view_permission(self, request, obj=None):
        # Superadmin can view all models
        if request.user.groups.filter(name='Superadmin').exists():
            return True
        
        # Admin can only view the 'Group' model
        if request.user.groups.filter(name='Admin').exists():
            if self.model == Group:
                return True
            return False
        
        # Other users can't view any models
        return False


# Register models for restricted access
@admin.register(Project)
class ProjectAdmin(GroupRestrictedAdmin):
    pass


@admin.register(Todolist)
class TodolistAdmin(GroupRestrictedAdmin):
    pass


@admin.register(TodolistFile)
class TodolistFileAdmin(GroupRestrictedAdmin):
    pass


@admin.register(MessageReply)
class MessageReplyAdmin(GroupRestrictedAdmin):
    pass


@admin.register(Message)
class MessageAdmin(GroupRestrictedAdmin):
    pass


@admin.register(Group)
class GroupAdmin(GroupRestrictedAdmin):
    pass


@admin.register(GroupMembership)
class GroupMembershipAdmin(GroupRestrictedAdmin):
    pass


@admin.register(GroupMessage)
class GroupMessageAdmin(GroupRestrictedAdmin):
    pass


@admin.register(chatLoginHistory)
class ChatLoginHistoryAdmin(GroupRestrictedAdmin):
    pass


@admin.register(ActionLog)
class ActionLogAdmin(GroupRestrictedAdmin):
    list_display = ('user', 'action', 'model_name', 'object_id', 'object_repr', 'timestamp')
    list_filter = ('action', 'model_name', 'timestamp')
    search_fields = ('object_repr', 'user__username')


@admin.register(LogEntry)
class LogEntryAdmin(GroupRestrictedAdmin):
    pass
