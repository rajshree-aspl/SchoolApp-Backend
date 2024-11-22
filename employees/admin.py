from django.contrib import admin
from .models import Employee

# Register your models here.


from django.contrib import admin
from .models import Employee

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('empid', 'fname', 'lname', 'gender', 'dob', 'address', 'email', 'phone_number', 
                    'date_of_joining', 'createdat', 'updatedat', 'schoolid')
    
    def schoolid(self, obj):
        return obj.schoolid
    schoolid.short_description = 'School'

    search_fields = ('fname', 'lname', 'email', 'phone_number')
    list_filter = ('gender', 'empid' ,'schoolid')
    readonly_fields = ('createdat', 'updatedat')  

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('user', 'empid', 'fname', 'lname', 'gender', 'dob', 'address', 'email', 
                       'phone_number', 'date_of_joining', 'schoolid'),
        }),
    )

    ordering = ('createdat',)
    filter_horizontal = ()
