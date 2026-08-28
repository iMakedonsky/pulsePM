from django.contrib import admin

from .models import WorkItem


@admin.register(WorkItem)
class WorkItemAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    list_display = ('title', 'workspace', 'status', 'priority', 'due_date')
    list_filter = ('status', 'priority')
    readonly_fields = ('id', 'created_at', 'last_update')
