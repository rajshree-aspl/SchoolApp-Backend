
# from django.shortcuts import render
from django.db.models import Avg,Count,Q, FloatField, ExpressionWrapper,F
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.urls import reverse 
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseBadRequest
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from rest_framework.response import Response
from django.shortcuts import render, redirect
from .utils import send_registration_email
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
from datetime import timedelta,date
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from students.models import School,Student
from django.http import Http404
from academics.models import Marks,Subject
from django.utils.timezone import now
from rest_framework.exceptions import NotFound
from students.serializers import StudentSerializer
from .serializers import CustomTokenObtainPairSerializer, CustomTokenRefreshSerializer, CustomTokenBlacklistSerializer,AdminUserRegistrationSerializer,CompleteRegistrationSerializer
from user.models import User, RegistrationLink
from students.models import Attendance,Class,Event
from user.serializers import ParentSerializer,UserSerializer, LoginSerializer
from user.custom_auth import AdminPermission,TeacherPermission
from employees.models import Employee
from django.urls import reverse
from .serializers import EmployeeSerializer

import uuid
from django.contrib.auth import get_user_model
from students.models import Section

User = get_user_model()

from .utils import get_holidays_for_month  # Import the utility function

class HolidaysListView(APIView):
    def get(self, request):
        month = request.query_params.get('month')
        year = request.query_params.get('year')
        country = request.query_params.get('country', 'US')

        if not month or not year:
            return Response({"detail": "Year and month are required parameters."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            month = int(month)
            year = int(year)
            if month < 1 or month > 12:
                return Response({"detail": "Month must be between 1 and 12."}, status=status.HTTP_400_BAD_REQUEST)
        except ValueError:
            return Response({"detail": "Invalid year or month format."}, status=status.HTTP_400_BAD_REQUEST)

        holidays = get_holidays_for_month(year, month, country)

        if holidays:
            return Response(holidays, status=status.HTTP_200_OK)
        return Response({"detail": "No holidays found for the specified month."}, status=status.HTTP_404_NOT_FOUND)

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = serializer.user

            user = User.objects.get(email=user)
            token = serializer.validated_data
            refresh_token = RefreshToken.for_user(user)

            response_data = {
                'access': str(token['access']),
                'refresh': str(refresh_token),
                'is_admin': user.is_admin
            }
            user.last_login = timezone.now()
            user.save()
            return Response(response_data, status=status.HTTP_200_OK)
        except Exception:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            token = serializer.validated_data
            refresh_token = RefreshToken.for_user(user)
            response_data = {
                'access': str(token['access']),
                'refresh': str(refresh_token),
            }
            return Response(response_data, status=status.HTTP_200_OK)

class CustomTokenRefreshView(TokenRefreshView):
    serializer_class = CustomTokenRefreshSerializer




# class AdminRegisterUserView(APIView):
#     permission_classes=[AdminPermission]
#     def post(self, request, format=None):
#         print("Request Data:", request.data) 
#         serializer = AdminUserRegistrationSerializer(data=request.data)

#         if serializer.is_valid():
#             reg_id = str(uuid.uuid4())
#             while User.objects.filter(reg_id=reg_id).exists():
#                 reg_id = str(uuid.uuid4())
#             validated_data = serializer.validated_data
#             validated_data['reg_id'] = reg_id

#             date_of_admission = validated_data.pop('date_of_admission', None)
#             class_sec = validated_data.pop('class_sec', None)
#             user = User.objects.create_user(**validated_data)
#             print("User created successfully:", user)
            
#             admin_schoolid = request.user.schoolid
#             print("Class Section Value:", class_sec)
                  
#             section = Section.objects.filter(clssectionid=class_sec).first()
#             if section:
#                 class_section_str = section.clssectionid
#             else:
#                 print("No matching section found for:", class_sec)
#                 class_section_str = 'UNKNOWN'

#             date_of_admission_str = date_of_admission.strftime('%m%Y') if date_of_admission else '000000'

#             # Get the section identifier from the section object (can be class-section)
#             # class_section_str = section.cls_section_id if section else 'UNKNOWN'
             
#             studentid = f"{admin_schoolid}ST{user.reg_id[:4].upper()}{date_of_admission_str}{class_section_str}"
#             Student.objects.create(user=user,
#                                 studentid=studentid,
#                                 date_of_admission=date_of_admission,
#                                 clssectionid=section)
            
#             print("Student created successfully")
                        
#             token = urlsafe_base64_encode(force_bytes(user.email))
#             RegistrationLink.objects.create(user=user, token=token)
#             frontend_registration_link = f"http://localhost:3000/userform/{token}/"
#             send_registration_email(user.email, frontend_registration_link)
#             return Response({'registration_link': frontend_registration_link}, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
# class AdminRegisterUserView(APIView):
#     permission_classes = [AdminPermission]

#     def post(self, request, format=None):
#         print("Request Data:", request.data)
#         serializer = AdminUserRegistrationSerializer(data=request.data)

#         if serializer.is_valid():
#             reg_id = str(uuid.uuid4())
#             while User.objects.filter(reg_id=reg_id).exists():
#                 reg_id = str(uuid.uuid4())
#             validated_data = serializer.validated_data
#             validated_data['reg_id'] = reg_id
#             full_name = validated_data.get('fullName', '')
#             fname_initials = full_name.split(' ')[0][:3].upper()  # Extract initials from the first part of the full name
#             print(f"Extracted First Name Initials: {fname_initials}")

#             date_of_admission = validated_data.pop('date_of_admission', None)
#             class_sec = validated_data.pop('class_sec', None)
#             user = User.objects.create_user(**validated_data)
#             print("User created successfully:", user)
           

#             admin_school = request.user.schoolid
#             admin_schoolcode = admin_school.schoolcode 
#             print("Class Section Value:", class_sec)

#             try:
#                 class_id_str = class_sec[:-1]  
#                 section_name = class_sec[-1]   

#                 class_instance = Class.objects.filter(classname=class_id_str).first()
#                 if class_instance:
#                     section_instance = Section.objects.filter(sectionname=section_name, classid=class_instance).first()
#                 else:
#                     section_instance = None
#             except Exception as e:
#                 print(f"Error parsing class_sec: {e}")
#                 section_instance = None

#             if section_instance:
#                 # class_section_str = section_instance.clssectionid
#                 class_section_str = f"{class_id_str}-{section_name}"
#             else:
#                 print("No matching section found for:", class_sec)
#                 class_section_str = 'UNKNOWN'

#             date_of_admission_str = date_of_admission.strftime('%m%Y') if date_of_admission else '000000'
#             studentid = f"{admin_schoolcode}ST{fname_initials}{user.reg_id[:4].upper()}{class_section_str}{date_of_admission_str}"
#             Student.objects.create(
#                 user=user,
#                 studentid=studentid,
#                 date_of_admission=date_of_admission,
#                 clssectionid=section_instance
#             )

#             print("Student created successfully")

#             token = urlsafe_base64_encode(force_bytes(user.email))
#             RegistrationLink.objects.create(user=user, token=token)
#             frontend_registration_link = f"http://localhost:3000/userform/{token}/"
#             send_registration_email(user.email, frontend_registration_link)
#             return Response({'registration_link': frontend_registration_link}, status=status.HTTP_201_CREATED)

#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# class AdminRegisterUserView(APIView):
#     permission_classes = [AdminPermission]

#     def post(self, request, format=None):
#         print("Request Data:", request.data)
#         serializer = AdminUserRegistrationSerializer(data=request.data)

#         if serializer.is_valid():
#             reg_id = str(uuid.uuid4())
#             while User.objects.filter(reg_id=reg_id).exists():
#                 reg_id = str(uuid.uuid4())
#             validated_data = serializer.validated_data
#             validated_data['reg_id'] = reg_id

#             full_name = validated_data.get('fullName', '')
#             fname_initials = full_name.split(' ')[0][:3].upper()  
#             print(f"Extracted First Name Initials: {fname_initials}")

#             date_of_admission = validated_data.pop('date_of_admission', None)
#             class_sec = validated_data.pop('class_sec', None)
#             user = User.objects.create_user(**validated_data)
#             print("User created successfully:", user)

           
#             user_role = 'S' if validated_data.get('user_type') == 'student' else 'O'  # Default to 'O' if not student

          
#             if date_of_admission:
#                 month_year_str = date_of_admission.strftime('%m%y').upper()
#             else:
#                 month_year_str = '0000'  
#             system_generated_user_id = reg_id[-4:]  

#             studentid = f"{fname_initials}{user_role}{month_year_str}{system_generated_user_id}"
            
#             if '-' in class_sec:
#                 class_id_str, section_name = class_sec.split('-')
#             else:
#                 class_id_str = class_sec[:-1]
#                 section_name = class_sec[-1]

#             print(f"Parsed class_id: {class_id_str}, section_name: {section_name}")

#             try:
#                 class_instance = Class.objects.filter(classname=class_id_str).first()
#                 if class_instance:
#                     section_instance = Section.objects.filter(sectionname=section_name, classid=class_instance).first()
#                 else:
#                     section_instance = None
#             except Exception as e:
#                 print(f"Error parsing class_sec: {e}")
#                 section_instance = None

#             if section_instance:
#                 class_section_str = f"{class_id_str}-{section_name}"
#             else:
#                 print("No matching section found for:", class_sec)
#                 class_section_str = 'UNKNOWN'
#             Student.objects.create(
#                 user=user,
#                 studentid=studentid,
#                 date_of_admission=date_of_admission,
#                 clssectionid=section_instance ,
#                 email=user.email,
#                 phone_number=user.phone_number,
#                 dob=user.dob,
                

#             )

#             print("Student created successfully with ID:", studentid)

#             token = urlsafe_base64_encode(force_bytes(user.email))
#             RegistrationLink.objects.create(user=user, token=token)
#             frontend_registration_link = f"http://localhost:3000/userform/{token}/"
#             send_registration_email(user.email, frontend_registration_link)
#             return Response({'registration_link': frontend_registration_link}, status=status.HTTP_201_CREATED)

#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




# class AdminRegisterUserView(APIView):
#     permission_classes = [AdminPermission]

#     def post(self, request, format=None):
#         print("Request Data:", request.data)
#         serializer = AdminUserRegistrationSerializer(data=request.data)

#         if serializer.is_valid():
#             reg_id = str(uuid.uuid4()) 
#             while User.objects.filter(reg_id=reg_id).exists():
#                 reg_id = str(uuid.uuid4())
#             validated_data = serializer.validated_data
#             validated_data['reg_id'] = reg_id

#             # full_name = validated_data.get('fullName', '')
#             fname=validated_data.get('fname','')
            
#             fname_initials = fname.split(' ')[0][:3].upper()  
#             print(f"Extracted First Name Initials: {fname_initials}")

#             date_of_admission = validated_data.pop('date_of_admission', None)
#             date_of_joining=validated_data.pop('date_of_joining',None)
#             class_id_str = validated_data.pop('classid', None)  # Extract classid directly from the request
#             user = User.objects.create_user(**validated_data)
#             print("User created successfully:", user)

#             user_role = 'S' if validated_data.get('user_type') == 'student' else 'E'  # Default to 'O' if not student

#             if date_of_admission:
#                 month_year_str = date_of_admission.strftime('%m%y').upper()
#             elif date_of_joining:
#                 month_year_str=date_of_joining.strftime('%m%y').upper()
#             else:
#                 month_year_str = '0000'  
#             system_generated_user_id = reg_id[-4:] 

#             studentid = f"{fname_initials}{user_role}{month_year_str}{system_generated_user_id}"
#             empid= f"{fname_initials}{user_role}{month_year_str}{system_generated_user_id}"

#             # Get Class instance using class_id_str
#             try:
#                 class_instance = Class.objects.filter(classid=class_id_str).first()
#             except Exception as e:
#                 # print(f"Error fetching class instance: {e}")
#                 class_instance = None

#             if class_instance:
#                 print(f"Class instance found: {class_instance}")
#             else:
#                 # print(f"No matching class found for class_id: {class_id_str}")
#                 return Response({"error": "Invalid classid"}, status=status.HTTP_400_BAD_REQUEST)

            
#             if validated_data.get('user_type') == 'teacher':
#                 # Create Teacher instance
#                 Teacher.objects.create(
#                     user=user,
#                     empid=empid,
#                     fname=validated_data.get('fname'),
#                     lname=validated_data.get('lname'),
#                     dob=user.dob,
#                     phone_number=user.phone_number,
#                     date_of_joining=date_of_joining,
#                     email=user.email
#                 )
#                 print("Teacher created successfully with ID:", empid)


#             Student.objects.create(user=user,
#                 studentid=studentid,
#                 date_of_admission=date_of_admission,  
#                 email=user.email,
#                 phone_number=user.phone_number,
#                 dob=user.dob,
#                 fname=validated_data.get('fname'),  # Ensure fname is saved
#                 lname=validated_data.get('lname') 
#             )
            
#             print("Student created successfully with ID:", studentid)

#             token = urlsafe_base64_encode(force_bytes(user.email))
#             RegistrationLink.objects.create(user=user, token=token)
#             frontend_registration_link = f"http://localhost:3000/userform/{token}/"
#             send_registration_email(user.email, frontend_registration_link)
#             return Response({'registration_link': frontend_registration_link}, status=status.HTTP_201_CREATED)

#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class AdminRegisterUserView(APIView):
    permission_classes = [AdminPermission]

    def post(self, request, format=None):
        print("Request Data:", request.data)
        serializer = AdminUserRegistrationSerializer(data=request.data)

        if serializer.is_valid():
            reg_id = str(uuid.uuid4()) 
            while User.objects.filter(reg_id=reg_id).exists():
                reg_id = str(uuid.uuid4())

            validated_data = serializer.validated_data
            validated_data['reg_id'] = reg_id
            admin_user = request.user
            admin_school = admin_user.schoolid

            fname = validated_data.get('fname', '')
            fname_initials = fname.split(' ')[0][:3].upper()  
            print(f"Extracted First Name Initials: {fname_initials}")

            date_of_admission = validated_data.pop('date_of_admission', None)
            date_of_joining = validated_data.pop('date_of_joining', None)
            employee_role = validated_data.pop('employee_role', None)
            class_id_str = validated_data.pop('classid', None)  

            # Attempt to retrieve the Class instance here for students
            class_instance = Class.objects.filter(classid=class_id_str).first() if class_id_str else None
            if validated_data.get('user_type') == 'student' and not class_instance:
                return Response({"error": "Invalid classid for student"}, status=status.HTTP_400_BAD_REQUEST)

            user = User.objects.create_user(**validated_data)
            print("User created successfully:", user)

            user_role = 'S' if validated_data.get('user_type') == 'student' else 'E'  
            month_year_str = (date_of_admission or date_of_joining).strftime('%m%y').upper()
            system_generated_user_id = reg_id[-4:]
            unique_id = f"{fname_initials}{user_role}{month_year_str}{system_generated_user_id}"

            # Create Employee or Student based on user_type
            if validated_data.get('user_type') == 'teacher':
                Employee.objects.create(
                    user=user,
                    empid=unique_id,
                    fname=validated_data.get('fname'),
                    lname=validated_data.get('lname'),
                    dob=user.dob,
                    phone_number=user.phone_number,
                    date_of_joining=date_of_joining,
                    email=user.email,
                    schoolid=admin_school
                )
                print("Teacher created successfully with ID:", unique_id)
            else:  # Student creation
                Student.objects.create(
                    user=user,
                    studentid=unique_id,
                    classid=class_instance,  # Pass the class instance
                    date_of_admission=date_of_admission,
                    email=user.email,
                    phone_number=user.phone_number,
                    dob=user.dob,
                    fname=validated_data.get('fname'),
                    lname=validated_data.get('lname'),
                    schoolid=admin_school
                )
                print("Student created successfully with ID:", unique_id)

            # Generate registration link and send email
            token = urlsafe_base64_encode(force_bytes(user.email))
            RegistrationLink.objects.create(user=user, token=token)
            frontend_registration_link = f"http://localhost:3000/userform/{token}/"
            send_registration_email(user.email, frontend_registration_link)
            return Response({'registration_link': frontend_registration_link}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class RegistrationLinkView(APIView):

    def post(self, request, token, format=None):
        try:
            email = force_str(urlsafe_base64_decode(token))
            user = User.objects.get(email=email)
            print(f"User found: {user.email}")

            registration_link = RegistrationLink.objects.filter(user=user, token=token, is_used=False).first()
            if not registration_link:
                return Response({'error': 'Invalid or already used registration link.'}, status=status.HTTP_400_BAD_REQUEST)

            serializer = CompleteRegistrationSerializer(data=request.data, instance=user)
            if serializer.is_valid():
                serializer.save()

                if user.user_type == 'student':
                    Student.objects.get_or_create(user=user)
                elif user.user_type == 'teacher':
                    Employee.objects.get(user=user)
                
                registration_link.is_used = True
                registration_link.save()
                return Response({'message': 'Registration completed successfully.'}, status=status.HTTP_200_OK)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except User.DoesNotExist:
            return Response({'error': 'Invalid registration link'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(f"Error during registration: {e}")
            return Response({'error': 'An unexpected error occurred'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get(self, request, token, format=None):
        try:
            email = force_str(urlsafe_base64_decode(token))
            user = User.objects.get(email=email)
            registration_link = RegistrationLink.objects.filter(user=user, token=token).first()

            if not registration_link:
                return Response({'error': 'Invalid registration link'}, status=status.HTTP_400_BAD_REQUEST)

            user_data = {
                'email': user.email,
                'user_type': user.user_type,
                'phone_number': str(user.phone_number),
                'dob': user.dob,
                'reg_id': user.reg_id,
                'password': '',
                'confirm_password': ''
            }

            if user.user_type == 'student':
                student_profile, _ = Student.objects.get_or_create(user=user)
                user_data.update({
                    'first_name': student_profile.fname,
                    'last_name': student_profile.lname,
                    'studentid': student_profile.studentid,
                    'date_of_admission': student_profile.date_of_admission,
                })
            elif user.user_type == 'teacher':
                teacher_profile = Employee.objects.get(user=user)
                user_data.update({
                    'first_name': teacher_profile.fname,
                    'last_name': teacher_profile.lname,
                    'empid': teacher_profile.empid,
                    'date_of_joining': teacher_profile.date_of_joining,
                })

            return Response(user_data, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response({'error': 'Invalid registration link'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(f"Error during token verification: {e}")
            return Response({'error': 'An unexpected error occurred'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)





  

class AdminUpdateStudentProfileView(APIView):
    permission_classes = [IsAuthenticated, AdminPermission]
    def post(self, request, studentid, format=None):
        student_profile = get_object_or_404(Student,studentid=studentid) 

       

        data = {
            'user': student_profile.user.id,
            'email':  student_profile.user.email,
            'fname': student_profile.user.fname,
            'lname': student_profile.user.lname,
            'dob':  student_profile.user.dob,
            'date_of_admission': student_profile.date_of_admission,  # Access studentid from student_profile
            'createdat': student_profile.createdat or timezone.now(),
            'updatedat': timezone.now(),
        }

        serializer = StudentSerializer(student_profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            message = "Student profile updated successfully" 
            return Response({"message": message}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        




    


class LoginView(APIView):
    permisson_clases= [IsAuthenticated]

    def post(self, request, format=None):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            access = CustomTokenObtainPairSerializer().get_token(user)
            refresh_token = RefreshToken.for_user(user)
            user_type = getattr(user,'user_type', 'unknown')
            fname = getattr(user,'fname','null')
            lname = getattr(user,'lname','null')
            today = timezone.now().date()
            if user_type != 'student':
                # Create attendance only if the record for today does not exist
                if not Attendance.objects.filter(user=user, date=today).exists():
                    Attendance.objects.create(user=user, status='Present', date=today)

            return Response({
                'msg': f'Welcome {user_type.capitalize()}!',
                'user_type': user_type,
                'token': {
                    'access': str(access.access_token),
                    'refresh': str(refresh_token),
                },
                'fname':fname,
                'lname':lname,
            }, status=status.HTTP_200_OK)

        return Response({'msg': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    




class AdminProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        try:
            if pk:
                admin = User.objects.get(pk=pk, user_type='admin')
                serializer = UserSerializer(admin)
            else:
                admins = User.objects.filter(user_type='admin')
                serializer = UserSerializer(admins, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'error': 'Admin not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


        

class TeacherProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        try:
            if pk:
                teachers = User.objects.get(pk=pk, user_type='teacher')
                serializer = UserSerializer(teachers)
            else:
                teachers = User.objects.filter(user_type='teacher')
                serializer = UserSerializer(teachers, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'error': 'Teacher not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class ParentProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        try:
            if pk:
                parent = User.objects.get(pk=pk, user_type='parent')
                serializer = UserSerializer(parent)
            else:
                parents = User.objects.filter(user_type='parent')
                serializer = UserSerializer(parents, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'error': 'Parent not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
from user.renderers import UserRenderer
from user.serializers import UserProfileSerializer


class UserProfileView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        try:
            # Get the authenticated user
            user = request.user
            # Serialize the user data with context
            serializer = UserProfileSerializer(user, context={"user": user})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"msg": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class AdminDashboardView(APIView):
    permission_classes=[IsAuthenticated,AdminPermission]
    
    def get(self, request):
        try:
            current_year = now().year

            today = date.today()

            total_attendance = Attendance.objects.filter(date=today).count()
            present_attendance = Attendance.objects.filter(date=today, status='Present').values('user__user_type').annotate(count=Count('id'))
            # attendance_rate = (present_attendance / total_attendance) * 100 if total_attendance > 0 else 0
            print(present_attendance)
        
            active_teachers =Employee.objects.filter(createdat__year__lte=current_year )
            total_teachers = active_teachers.count()
        

            total_classes = Class.objects.count()

        
            # students_logged_in = Attendance.objects.filter(user__user_type='student', date=today).count()
            # teachers_logged_in = Attendance.objects.filter(user__user_type='teacher', date=today).count()

            data = {
                'todays_attendance': [{i["user__user_type"]:i["count"]} for i in present_attendance ],
                
                
                'total_teachers': total_teachers,
                'total_classes': total_classes,
                # 'students_logged_in': students_logged_in,
                # 'teachers_logged_in': teachers_logged_in,
            }

        
        

            return Response(data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    



class DemographicsView(APIView):
    permission_classes=[IsAuthenticated,AdminPermission]

    def get(self, request):
        try:
            gender_data = Student.objects.values('gender').annotate(count=Count('studentid'))
            

            data = {
                'male': 0,
                'female': 0,
            }
            
            
            for entry in gender_data:
                gender = entry['gender'].lower()  
                if gender == 'male':
                    data['male'] = entry['count']
                elif gender == 'female':
                    data['female'] = entry['count']
            
            return Response(data, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    

class AttendanceView(APIView):
    permission_classes=[IsAuthenticated,AdminPermission]
    def get(self, request):
        try:
            attendance_data = Attendance.objects.select_related('class_section').values('class_section__sectionname').annotate(
                total_students=Count('user', distinct=True),
                total_present=Count('user', filter=Q(status='Present'), distinct=True),
                attendance_percentage=ExpressionWrapper(
                    F('total_present') * 100.0 / F('total_students'),
                    output_field=FloatField()
                )
            )

            data = list(attendance_data)

            if not data:
                raise NotFound("No attendance data found")

            return Response(data, status=status.HTTP_200_OK)

        except NotFound as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
class PerformanceAnalyticsView(APIView):
    permission_classes=[IsAuthenticated,AdminPermission]
    def get(self, request):
        data = []
        subjects = Subject.objects.all()  
        for subject in subjects:
            subject_data = Marks.objects.filter(subjectid=subject).aggregate(
                first_class=Count('marksid', filter=Q(marksobtained__gte=75)),
                failed=Count('marksid', filter=Q(marksobtained__lt=40)),
                minimum_marks=Count('marksid', filter=Q(marksobtained__gte=40, marksobtained__lt=75))
            )
            data.append({
                'subject': subject.subjectname,
                'first_class': subject_data['first_class'],
                'failed': subject_data['failed'],
                'minimum_marks': subject_data['minimum_marks']
            })

        return Response(data)
    


class CalendarEventsView(APIView):
    permission_classes=[IsAuthenticated,AdminPermission]
    def get(self, request):
        try:
            start_date = request.query_params.get('start_date', None)
            end_date = request.query_params.get('end_date', None)

            if start_date and end_date:
                events = Event.objects.filter(start_date__gte=start_date, end_date__lte=end_date)
            else:
                events = Event.objects.all()

            if not events.exists():
                raise NotFound("No events found for the specified period")

            serializer = EventSerializer(events, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except NotFound as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

class PasswordResetView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        email = request.data.get('email')
        if not email:
            return Response({'msg': 'Email is required.'}, status=status.HTTP_400_BAD_REQUEST)

        reset_code = get_random_string(6)
        try:
            user = User.objects.get(email=email)
            user.reset_code = reset_code
            user.save()

            send_mail(
                'Password Reset Request',
                f'Your password reset code is: {reset_code}',
                'noreply@example.com',
                [email],
            )

            return Response({'msg': 'Password reset email has been sent.'}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'msg': 'Email not found.'}, status=status.HTTP_404_NOT_FOUND)

class PasswordResetConfirmView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        reset_code = request.data.get('reset_code')
        new_password = request.data.get('new_password')
        confirm_password = request.data.get('confirm_password')

        if not  reset_code or not new_password:
            return Response({'msg':  'Reset code, and new password are required.'}, status=status.HTTP_400_BAD_REQUEST)
        



        if new_password != confirm_password:
            return Response(
                {'msg': 'New password and confirm password do not match.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(reset_code=reset_code)
        except User.DoesNotExist:
            return Response({'msg': 'Invalid reset code.'}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.reset_code = ''
        user.save()

        return Response({'msg': 'Password has been reset successfully.'}, status=status.HTTP_200_OK)

class LogoutView(APIView):

    def post(self, request, format=None):
        serializer = CustomTokenBlacklistSerializer(data=request.data)
        if serializer.is_valid():
            return Response({'msg': "Logout successful"}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors,  status=status.HTTP_400_BAD_REQUEST)
        

class DeleteUserView(APIView):
    permission_classes = [IsAuthenticated, AdminPermission]  # Admin permissions required

    def delete(self, request, user_id, format=None):
        try:
            user = User.objects.get(id=user_id) 
            
            user.delete()
            
            return Response({"message": "User (and associated student profile) deleted successfully."}, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response({"error": "User does not exist."}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class DeleteBlacklistAdOutstandingView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        try:
            user = request.user
            if user.is_superuser:
                outstanding, _ = OutstandingToken.objects.filter(expires_at__lte=timezone.now()).delete()
                blacklist, _ = BlacklistedToken.objects.filter(token__created_at__lte=timezone.now() - timedelta(minutes=10)).delete()
                return Response({'msg': f'Deleted {outstanding} outstanding tokens and {blacklist} blacklisted tokens.'}, status=status.HTTP_200_OK)
            return Response({'msg': "You have no permission."}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'msg': str(e)}, status=status.HTTP_400_BAD_REQUEST)



 





 