from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User

class UserAdmin(BaseUserAdmin):
    # The forms to add and change user instances

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ["email", "is_admin", "fname","lname","is_staff",  "is_active", "user_type","dob","phone_number",'schoolid','is_superuser']
    list_filter = ["is_admin", "user_type","email",'is_superuser']
    readonly_fields = ('date_created','date_updated',"reg_id")  
    fieldsets = [
        (None, {"fields": ["email", "password"]}),
        ("Personal info", {"fields": ["fname","lname","dob","phone_number",  "user_type"]}),
        ("Permissions", {"fields": ["is_admin", "is_staff", "is_active", "is_superuser"]}),
        
    ]
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = [
        (
            None,
            {
                "classes": ["wide"],
                "fields": ["email", "password1", "is_staff", "is_active",  "password2","fname","lname" ,"user_type","dob","phone_number","date_created","date_updated","reg_id",'schoolid','is_superuser']
            },
        ),
    ]
    search_fields = ["email"]
    ordering = ["email"]
    filter_horizontal = []
# class AttendanceAdmin(admin.ModelAdmin):
#     list_display = ["id", "student", "date", "status", "remarks"]


# Now register the new UserAdmin...
admin.site.register(User, UserAdmin)
