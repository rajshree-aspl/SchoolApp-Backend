from django.contrib import admin
from .models import Subject,SubjectTeacher,Period,Exam,Marks,Result,ClassSchedule,Syllabus,SubjectTeacher,Timetable,AcademicYear

# Register your models here.
@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['subjectid', 'subjectname', 'subject_code', 'classid']

# Define and register the SyllabusAdmin
@admin.register(Syllabus)
class SyllabusAdmin(admin.ModelAdmin):
    list_display = ['subject', 'syllabus_text', 'updated_at']


@admin.register(Timetable)
class TimetableAdmin(admin.ModelAdmin):
    list_display = ['class_section','subject','teacher','day','time_slot']

@admin.register(AcademicYear)
class AcademicYear(admin.ModelAdmin):
    list_display=['year','start_date','end_date']


@admin.register(SubjectTeacher)
class SubjectTeacherAdmin(admin.ModelAdmin):
    list_display=['subject_teacher_id','subjectid','teacherid','clssectionid']
