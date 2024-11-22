from django.urls import path
from .views import AttendanceListView, AttendanceDetailView
from .views import (
    RegisterSchoolView,
    StudentProfileView,
    EditStudentDetailsView,
    UpdatePhotoRequestView,
    GenerateIDCardRequestView,
    ApproveRequestView,
    RejectRequestView,
    ParentInformationView,
    StudentHomepageView,
    TaskUpdateView,
    TaskDeleteView,
    TaskCreateView,
    AttendanceReportView,
   MonthWiseAttendanceView,
    NotificationView,
    UploadDocumentView,
    DownloadDocumentListView,
    LeaveApplicationView,
    HolidaysListView
)

urlpatterns = [
    path('register-school/', RegisterSchoolView.as_view(), name='register-school'),
    path('students/', StudentProfileView.as_view(), name='get_student_profile'),
    
    # Retrieve all students in a specific section using section_id
    path('students/section/<str:section_id>/', StudentProfileView.as_view(), name='get_students_by_section'),
    
    # Assign a section to a student
    path('students/<str:pk>/assign-section/', StudentProfileView.as_view(), name='assign_section_to_student'),

    path('student_edit_details/', EditStudentDetailsView.as_view(), name='edit-student-details'),
    path('students_update-photo/<str:student_id>/', UpdatePhotoRequestView.as_view(), name='update-student-photo'),
    path('students_update-photo/', UpdatePhotoRequestView.as_view(), name='update-student-photo'),
    path('generate-studentidcard/', GenerateIDCardRequestView.as_view(), name='generate-student-id-card'),
    path('admin-approve/<int:pk>/', ApproveRequestView.as_view(), name='approve-request'),
    path('admin-approve/', ApproveRequestView.as_view(), name='approve-request'),
    path('admin-reject/<int:pk>/', RejectRequestView.as_view(), name='reject-request'),

    path('parent/<str:student_id>/', ParentInformationView.as_view(), name='parent-information'),
    path('parent/', ParentInformationView.as_view(), name='parent-information'),

    path('students-homepage/<int:pk>/', StudentHomepageView.as_view(), name='student-homepage'),
    path('tasks/update/<int:pk>/', TaskUpdateView.as_view(), name='task-update'),
    path('tasks/create/<int:pk>/', TaskCreateView.as_view(), name='task-create'),
    path('tasks/delete/<int:pk>/', TaskDeleteView.as_view(), name='task-delete'),
    # path('attendance-history/<int:student_id>/',AttendanceHistoryView.as_view(),name='attendance-history'),
    path('monthly-attendance/<int:student_id>/<int:month>/',MonthWiseAttendanceView.as_view(),name='monthly-attendance'),
    # path('students/<int:student_id>/upload/', UploadDocumentView.as_view(), name='upload-document'),
    # path('students/<int:student_id>/documents/', DownloadDocumentListView.as_view(), name='download-document-list'),
    path('leaveapplication/', LeaveApplicationView.as_view(), name='leaveapply'),
    path('leaveapplication/<int:pk>/', LeaveApplicationView.as_view(), name='leaveapply'),
    path('holidays/', HolidaysListView.as_view(), name='holidays-list'),
    path('attendance-report/', AttendanceReportView.as_view(), name='attendance-report'),

    path('attendance/', AttendanceListView.as_view(), name='attendance-list'),
    path('attendance/<int:pk>/', AttendanceDetailView.as_view(), name='attendance-detail'),
    path('upload-document/<int:student_id>/', UploadDocumentView.as_view(), name='upload_document'),
    path('download-document/<str:student_id>/', DownloadDocumentListView.as_view(), name='download_document'),
    path('notifications/', NotificationView.as_view(), name='notification-list'),
    
       
]



