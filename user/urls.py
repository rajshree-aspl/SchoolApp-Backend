from django.urls import path,include
from .views import CustomTokenObtainPairView,PasswordResetView,LoginView,PasswordResetConfirmView,LogoutView,CustomTokenRefreshView
from .views import DeleteBlacklistAdOutstandingView,AdminRegisterUserView,RegistrationLinkView,AdminDashboardView,CalendarEventsView, UserProfileView,DeleteUserView
from .views import AdminDashboardView, DemographicsView, AttendanceView, PerformanceAnalyticsView, CalendarEventsView,AdminUpdateStudentProfileView,AdminProfileView,ParentProfileView, TeacherProfileView

# from .views import AttendanceListView, AttendanceDetailView
urlpatterns = [
   
    path('gettoken/',CustomTokenObtainPairView.as_view(), name= 'token_pair'),
       
    path('refresh-token/', CustomTokenRefreshView.as_view(), name= 'token_pair'),
   
    path('login/',LoginView.as_view(),name="login"),
    path('password_reset/',PasswordResetView.as_view(),name="password_reset"),
    path('password_confirm/',PasswordResetConfirmView.as_view(),name="password_confirm"),
    
    path('logout/',LogoutView.as_view(),name="logout"),
    path('delete-tokens/', DeleteBlacklistAdOutstandingView.as_view(), name='delete-tokens'),
    
    path('admin/register/', AdminRegisterUserView.as_view(), name='admin-register-user'),
    path('Registration/<str:token>/',RegistrationLinkView.as_view(), name='Registration-link'),


    

    # path('complete-registration/<str:token>/', CompleteRegistrationView.as_view(), name='complete-registration'),
   
    #  path('reportcard/', AttendanceReportCardListView.as_view(), name='attendance-report-card-list'),
    # path('reportcard/<int:pk>/', AttendanceReportCardDetailView.as_view(), name='attendance-report-card-detail'),

    
    path('admin/dashboard/', AdminDashboardView.as_view(), name='admin-dashboard'),
    path('admin/demographics/', DemographicsView.as_view(), name='demographics'),
    path('admin/attendance/', AttendanceView.as_view(), name='attendance'),
    path('admin/performance/', PerformanceAnalyticsView.as_view(), name='performance-analytics'),
    path('admin/events/', CalendarEventsView.as_view(), name='calendar-events'),


    # path('api/create-student/', CreateStudentView.as_view(), name='create-student'),
    path('admin/student-profile/<str:studentid>/', AdminUpdateStudentProfileView.as_view(), name='admin-update-student-profile'),

    path('user/profiles/<int:pk>/', UserProfileView.as_view(), name='User-profile'),
    path('user/profiles/', UserProfileView.as_view(), name='User-profile'),
    # path('user/profiles/email/<str:email>/', UserProfileView.as_view(), name='user-profile-by-email'),  # For email in URL

    path('profiles/admins/', AdminProfileView.as_view(), name='admin-profiles'),
    path('profiles/admins/<int:pk>/', AdminProfileView.as_view(), name='admin-profile-detail'),
    path('profiles/teachers/', TeacherProfileView.as_view(), name='teacher-profiles'),
    # path('profiles/teachers/<int:pk>/', TeacherProfileView.as_view(), name='teacher-profile-detail'),
    path('profiles/parents/', ParentProfileView.as_view(), name='parent-profiles'),
    path('profiles/parents/<int:pk>/', ParentProfileView.as_view(), name='parent-profile-detail'),

    path('admin/delete-user/<int:user_id>/', DeleteUserView.as_view(), name='delete_user'),
                                
]