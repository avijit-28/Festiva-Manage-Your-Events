from django.contrib import admin
# from .models import JobApplication

# from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, JobApplication, Event, Ticket, Category

class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'role', 'is_active', 'is_staff')
    list_filter = ('role', 'is_active', 'is_staff')
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'phone', 'bio', 'profile_picture')}),
        ('Permissions', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'first_name', 'last_name', 'role'),
        }),
    )
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)



# @admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'position', 'applied_at', 'status')
    list_filter = ('status', 'position', 'employment_type')
    search_fields = ('first_name', 'last_name', 'email', 'position')
    readonly_fields = ('applied_at',)
    date_hierarchy = 'applied_at'


# Register your models here
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Event)
admin.site.register(Ticket)
admin.site.register(Category)
admin.site.register(JobApplication)