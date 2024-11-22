from django.urls import path
from .views import DayTimetableView,  MonthTimetableView,WeekTimetableView,TeacherTimetableView
from .views import GetStudentsView,TeacherAttendanceView,TeacherAttendanceIndiviualView,AddClassView,AddSubjectView,TimetableView

urlpatterns = [
    path('timetable/day/<int:student_id>/', DayTimetableView.as_view(), name='day-timetable'),
    # path('timetable/week/<int:student_id>/', WeekTimetableView.as_view(), name='week-timetable'),
    path('timetable/month/<int:student_id>/<int:month>/<int:year>/', MonthTimetableView.as_view(), name='month-timetable'),
    path('academics/timetable/week/<int:student_id>/', WeekTimetableView.as_view(), name='week-timetable'),
    path('timetable/today/<int:teacher_id>/', TeacherTimetableView.as_view(), name='today-timetable'),

    # path('subjects/', CreateSubjectView.as_view(), name='create_subject'),  # POST for creating, GET for listing subjects
    # path('subjects/<int:pk>/', CreateSubjectView.as_view(), name='update_subject'),  # PATCH for updating a subject

    # path('classes/', CreateClassView.as_view(), name='create_class'),  # POST for creating, GET for listing classes
    # path('classes/<int:pk>/', CreateClassView.as_view(), name='update_class'),  # PATCH for updating a class

    # path('sections/', CreateSectionView.as_view(), name='create_section'),  # POST for creating, GET for listing sections
    # path('sections/<int:pk>/', CreateSectionView.as_view(), name='update_section'), 
    path('individual/attendance/', TeacherAttendanceIndiviualView.as_view(), name='individual_attendance'),
    path('attendance/<str:section_id>/', TeacherAttendanceView.as_view(), name='teacher_attendance'),
    path('attendances/', TeacherAttendanceView.as_view(), name='attendance-update'),
    path('students/<int:class_id>/<int:section_id>/', GetStudentsView.as_view(), name='get-students'),


    path('classes/', AddClassView.as_view(), name='add-class'),            # POST for adding class
    path('classes/<int:class_id>/', AddClassView.as_view(), name='edit-class'),  # PUT for editing a class
    path('subjects/add/', AddSubjectView.as_view(), name='add_subject'),
    path('subjects/<int:pk>/', AddSubjectView.as_view(), name='edit_subject'),
    path('subjects/', AddSubjectView.as_view(), name='edit_subject'),
    path('timetable/', TimetableView.as_view(), name='timetable-view'),

]



