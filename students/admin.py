from django.contrib import admin
from .models import Student, Parent, School, Class, Section, Task, Adminrequest, LeaveApplication,Holiday,ClassTeacher,MedicalInfo,EmergencyContact,Event,StudentParent,Attendance
# user/admin.py

from django.contrib import admin
from .models import Student

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('studentid', 'fname', 'lname', 'cls_section_id','classid','gender', 'dob', 'address','email','date_of_admission',
                    'createdat', 'updatedat', 'schoolid', 'current_grade', 'academic_year',
                    'nationality', 'religion', 'languages_spoken', 'state', 'city', 'pin', 'country', 'phone_number',
                    'photo_id')
    
    def cls_section_id(self, obj):
        return obj.cls_section_id
    cls_section_id.short_description = 'Class-Section'
    search_fields = ('fname', 'lname', 'email', 'phone_number')
    list_filter = ('gender', 'schoolid')
    readonly_fields = ('createdat', 'updatedat')  

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('user', 'fname', 'lname', 'gender', 'dob', 'address', 'email', 'phone_number','classid'
                       'schoolid','cls_section_id', 'current_grade', 'academic_year', 'nationality', 'religion',
                       'languages_spoken', 'state', 'city', 'pin', 'country', 'photo_id'),
        }),
    )

    search_fields = ('fname', 'lname', 'email', 'phone_number')
    ordering = ('createdat',)
    filter_horizontal = ()




class AdminrequestAdmin(admin.ModelAdmin):
    list_display = ["id", "requested_user", "student", "purpose", "data", "status"]

admin.site.register(Adminrequest, AdminrequestAdmin)

class ClassAdmin(admin.ModelAdmin):
    list_display = ["classid", "classname","createdat", "updatedat","classcode"]

admin.site.register(Class, ClassAdmin)

class ParentAdmin(admin.ModelAdmin):
    list_display = [
        "parentid", "mother_name","father_name","mother_dob","father_dob",
        "address", "mother_contactno", "father_contactno","email", "createdat", "updatedat", 
    ]

admin.site.register(Parent, ParentAdmin)

class SchoolAdmin(admin.ModelAdmin):
    list_display = ["schoolid", "schoolname", "schoolcode", "createdat", "updatedat"]

admin.site.register(School, SchoolAdmin)

class SectionAdmin(admin.ModelAdmin):
    list_display = ["clssectionid", "sectionname", "classid", "createdat", "updatedat"]

admin.site.register(Section, SectionAdmin)

class TaskAdmin(admin.ModelAdmin):
    list_display = ["id", "student", "task_description", "is_mandatory", "is_completed", "created_at"]

admin.site.register(Task, TaskAdmin)



class HolidayAdmin(admin.ModelAdmin):
    list_display=["holiday_id","date","description"]
admin.site.register(Holiday,HolidayAdmin)

class AttendanceAdmin(admin.ModelAdmin):
    list_display=["user","date","session_type","status"]
admin.site.register(Attendance,AttendanceAdmin)



admin.site.register(LeaveApplication)

admin.site.register(ClassTeacher)
admin.site.register(MedicalInfo)
admin.site.register(EmergencyContact)
admin.site.register(Event)
admin.site.register(StudentParent)