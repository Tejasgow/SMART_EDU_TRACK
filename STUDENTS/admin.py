from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Standard, Section, Student

# -------------------------------
# Standard Admin
# -------------------------------
@admin.register(Standard)
class StandardAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    search_fields = ['name']

# -------------------------------
#       Section Admin
# -------------------------------
@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'standard']
    list_filter = ['standard']
    search_fields = ['name']

# -------------------------------
# Student Admin
# -------------------------------
@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['id', 'get_full_name', 'user_email', 'standard', 'section', 'created_at']
    search_fields = ['user__first_name', 'user__last_name', 'user__email']
    list_filter = ['standard', 'section']

    def get_full_name(self, obj):
        return obj.user.get_full_name()
    get_full_name.short_description = 'Full Name'

    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'Email'
