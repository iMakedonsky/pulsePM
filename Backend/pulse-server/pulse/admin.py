from django.contrib import admin
from .models import *


# TODO: Output "id" each entity and and view fields separetors

class AccountAdmin(admin.ModelAdmin):
    readonly_fields = ('id',)
    fieldsets = [
        (
         {
            "fields": ["id", "username", ("first_name", "last_name"), "email", "password"]
         }),
        ("Date information", {"fields": ["created_at"]}),
    ]

class OrganizationAdmin(admin.ModelAdmin):
    readonly_fields = ('id',)
    fieldsets = [
        (None,
         {
             "fields": ["name", "owner_id", "content"]
         }),
        ("Date information", {"fields": ["description", "created_at"]}),
    ]

class MemberAdmin(admin.ModelAdmin):
    readonly_fields = ('id',)
    fieldsets = [
        (None,
         {
             "fields": ["id", "user_id", "owner_id", "role", "position", "location", "time_zone", "avatar", "last_activity_at"]
         }),
        ("Date information", {"fields": ["created_at"]}),
    ]

class WorkspaceAdmin(admin.ModelAdmin):
    readonly_fields = ('id',)
    fieldsets = [
        (None,
         {
            "fields": ["id", "name", "icon_url", "organization_id", "created_by", "space_code", "description"]
        }),
        ("Date information", {"fields": ["created_at"]}),
    ]

class WorkItemAdmin(admin.ModelAdmin):
    readonly_fields = ('id',)
    fieldsets = [
        (None,
         {
             "fields": ["id", "title", "status", "priority", "started_at", "due_date", "estimated_time", "time_spent"]
         }),
        ("Date information", {"fields": ["last_update", "created_at"], "classes": ["collapse"]}),
    ]

admin.site.register(Account)
admin.site.register(Organization)
admin.site.register(Member)
admin.site.register(WorkSpace)
admin.site.register(WorkItem)