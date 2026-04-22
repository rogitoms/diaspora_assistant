from django.contrib import admin
from .models import Task, Step, Message, StatusHistory

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display   = ["task_code", "intent", "status", "risk_score", "employee_team", "created_at"]
    list_filter    = ["intent", "status", "employee_team"]
    search_fields  = ["task_code", "original_request"]
    readonly_fields = ["task_code", "created_at", "updated_at"]

@admin.register(Step)
class StepAdmin(admin.ModelAdmin):
    list_display = ["task", "step_number", "description", "completed"]

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ["task", "channel"]

@admin.register(StatusHistory)
class StatusHistoryAdmin(admin.ModelAdmin):
    list_display = ["task", "old_status", "new_status", "changed_at"]