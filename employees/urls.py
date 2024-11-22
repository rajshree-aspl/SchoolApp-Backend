# from django.urls import path, include
# from .views import CustomTokenObtainPairView, CustomTokenRefreshView, EmployeeRegistrationView






# path('gettoken/',CustomTokenObtainPairView.as_view(), name= 'token_pair'),
# path('refreshtoken/', CustomTokenRefreshView.as_view(), name= 'token_resfresh'),
# path('register/', EmployeeRegistrationView.as_view(), name='register')



from django.urls import path
from .views import TeacherDashboardView,TeacherMyClassesView,ClassTeacherPageView,GetStudentsView,SubmitAttendanceView,AttendanceHistoryView,CreateOrUpdateEmergencyContactView,CreateOrUpdateMedicalInfoView,EmployeeView,AdminEmployeeClassesView,AssignSubjectTeachersView

urlpatterns = [
    path('teacher/dashboard/', TeacherDashboardView.as_view(), name='teacher-dashboard'),

    # path('student/profile/', StudentProfileView.as_view(), name='student-profile'),
    path('teacher/classes/', TeacherMyClassesView.as_view(), name='teacher-classes'),
    path('teacher/class/<int:class_id>/students/', ClassTeacherPageView.as_view(), name='get-students'),
    path('students/<int:section_id>/',GetStudentsView.as_view(), name=''),
    path('submit/attendance/', SubmitAttendanceView.as_view(), name='submit-attendnance'),
    path('attendance/history/<int:section_id>/', AttendanceHistoryView.as_view(), name='attendnance-history'),
    path('medical-info/<str:student_id>/', CreateOrUpdateMedicalInfoView.as_view(), name='create_medical_info'),
    path('medical-info/', CreateOrUpdateMedicalInfoView.as_view(), name='create_medical_info'),

    path('emergency-contact/<str:student_id>/', CreateOrUpdateEmergencyContactView.as_view(), name='create_emergency_contact'),
    path('emergency-contact/', CreateOrUpdateEmergencyContactView.as_view(), name='create_emergency_contact'),
    
   
    path('employees/', EmployeeView.as_view(), name='employee-list'),  # For GET all and POST
    path('employees/<str:pk>/', EmployeeView.as_view(), name='employee-detail'), 
    path('Admin/classes/', AdminEmployeeClassesView.as_view(), name='Admin-employeeclasses'), 
    # path('get/subjects/teachers/<int:class_id>/', AssignSubjectTeachersView.as_view(), name='get-subjectteacher'), 
    path('assign-teachers/', AssignSubjectTeachersView.as_view(), name='Assign-subjectteacher'), 
    path('assign-teachers/<int:classid>/<str:sectionid>/', AssignSubjectTeachersView.as_view(), name='get-subjectteacher'), 
    
]
    
    
    

    # path('teacher/student/<str:student_id>/', TeacherStudentProfileView.as_view(), name='teacher-student-profile'),
  

