from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from .models import Student, Adminrequest,Parent,School,Task
from .serializers import StudentSerializer, AdminrequestSerializer,ParentSerializer,TaskSerializer,StudentUpdateSerializer,AdminrequestlistSerializer,SchoolSerializer,LeaveApplicationRetrieveSerializer,LeaveApplicationSerializer
from rest_framework.permissions import IsAuthenticated
from user.custom_auth import StudentPermission,ParentPermission,TeacherPermission,AdminPermission
from .mongo_queries import handle_photo_upload
from django.core.files.uploadedfile import InMemoryUploadedFile
from students.mongo_queries import retrieve_photo
from bson.objectid import ObjectId 
from django.shortcuts import get_object_or_404
from .models import Student,  LeaveApplication, Holiday,User,Section
from .serializers import LeaveApplicationSerializer, HolidaySerializer,AttendanceReportSerializer,NotificationSerializer,AttendanceSerializer,ClassTeacherSerializer
from django.db.models.functions import ExtractMonth, ExtractYear
from students.models import Attendance
from django.utils.timezone import now 
from django.db.models import Count, Q
from .mongo_queries import upload_document,get_recent_documents
from .models import Notification,StudentParent,ClassTeacher
class RegisterSchoolView(APIView):
    permission_classes = [ AdminPermission]

    def post(self, request, format=None):
        serializer = SchoolSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# class StudentProfileView(APIView):
#     # permission_classes = [IsAuthenticated]

#     def get(self, request, pk=None, section_id=None):
#         try:
#             if pk:
#                 # Retrieve a specific student profile
#                 student = Student.objects.get(pk=pk)
#                 serializer = StudentSerializer(student)
#                 return Response(serializer.data)
#             elif section_id:
#                 # Retrieve all students in the specified section
#                 students = Student.objects.filter(clssectionid__clssectionid=section_id)
#                 serializer = StudentSerializer(students, many=True)
#                 return Response(serializer.data)
#             else:
#                 # Retrieve all students
#                 students = Student.objects.all()
#                 serializer = StudentSerializer(students, many=True)
#                 return Response(serializer.data)
        
#         except Student.DoesNotExist:
#             return Response({'error': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)
#         except Exception as e:
#             return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#     def post(self, request, pk=None):
#         try:
#             # Admin assigns a section to a student after registration
#             section_id = request.data.get('section_id')
#             if not pk or not section_id:
#                 return Response({"error": "Student ID and Section ID are required"}, status=status.HTTP_400_BAD_REQUEST)
            
#             # Fetch the student and section
#             student = Student.objects.get(pk=pk)
#             section = Section.objects.get(clssectionid=section_id)
            
#             # Assign the section
#             student.clssectionid = section
#             student.save()

#             return Response({"message": "Section assigned successfully"}, status=status.HTTP_200_OK)

#         except Student.DoesNotExist:
#             return Response({"error": "Student not found"}, status=status.HTTP_404_NOT_FOUND)
#         except Section.DoesNotExist:
#             return Response({"error": "Section not found"}, status=status.HTTP_404_NOT_FOUND)
#         except Exception as e:
#             return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
from django.db.models import F, Value, Case, When
from django.db.models.functions import Coalesce
from .models import Student, Section
from django.db import models
class StudentProfileView(APIView):
    def get(self, request):
        class_id = request.query_params.get('class_id')  # Primary filter by class_id
        section_id = request.query_params.get('section_id')  # Optional filter by section
        academic_year = request.query_params.get('academic_year')  # Optional filter by academic year
        student_id = request.query_params.get('student_id')
        try:
            if class_id:
                # Filter students based on class_id through Section relationship
                students = Student.objects.filter(classid__classid=class_id)
                print(f"Students after class_id filter ({class_id}):", students)

                # Apply optional academic year filter
                if academic_year:
                    students = students.filter(academic_year=academic_year)
                    print(f"Students after academic_year filter ({academic_year}):", students)

                # Apply optional section_id filter
                if section_id:
                    students = students.filter(clssectionid__clssectionid=section_id)
                    print(f"Students after section_id filter ({section_id}):", students)
                else:
                    # Annotate to indicate if a section is assigned
                    students = students.annotate(
                        assigned_section=Coalesce(F('clssectionid__sectionname'), Value("Unassigned")),
                        section_status=Case(
                            When(clssectionid__isnull=False, then=Value("Assigned")),
                            default=Value("Unassigned"),
                            output_field=models.CharField()
                        )
                    )
                    print("Annotated student list for section assignment:", students)

                # Serialize and return student data
                serializer = StudentSerializer(students, many=True)
                return Response(serializer.data)
            elif student_id:
                 try:
                    # print("sid",student_id) 
                    students = Student.objects.get(studentid=student_id)
                    print("target", students)
                    serializer = StudentSerializer(students)
                    return Response(serializer.data, status=status.HTTP_200_OK)
                 except ObjectDoesNotExist:
                    return Response({"error": "Student not found"}, status=status.HTTP_404_NOT_FOUND)
            else:
                students = Student.objects.all()
                serializer = StudentSerializer(students, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        student_ids = request.data.get('student_ids')  # List of student IDs
        section_id = request.data.get('section_id')  # Target section ID

        if not student_ids or not section_id:
            return Response({"error": "Student IDs and Section ID are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Fetch the section
            section = Section.objects.get(clssectionid=section_id)

            # Update the clssectionid for all students in a single query
            updated_students = Student.objects.filter(studentid__in=student_ids).update(clssectionid=section)

            # Check if any students were updated
            if updated_students == 0:
                return Response({"message": "No students were updated, please check the student IDs"}, status=status.HTTP_404_NOT_FOUND)

            return Response({"message": f"{updated_students} students assigned to section '{section.sectionname}' successfully"}, status=status.HTTP_200_OK)

        except Section.DoesNotExist:
            return Response({"error": "Section not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    def patch(self, request):
        student_ids = request.data.get('student_ids')  # List of student IDs
        section_id = request.data.get('section_id')  # Target section ID

        if not student_ids or not section_id:
            return Response({"error": "Student IDs and Section ID are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Fetch the section
            section = Section.objects.get(clssectionid=section_id)

            # Bulk update the clssectionid for multiple students
            updated_students = Student.objects.filter(studentid__in=student_ids).update(clssectionid=section)

            # Check if any students were updated
            if updated_students == 0:
                return Response({"message": "No students were updated, please check the student IDs"}, status=status.HTTP_404_NOT_FOUND)

            return Response({"message": f"{updated_students} students updated to section '{section.sectionname}' successfully"}, status=status.HTTP_200_OK)

        except Section.DoesNotExist:
            return Response({"error": "Section not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    



# class ParentInformationView(APIView):
    
#     def post(self, request, student_id=None, format=None):
#         if not student_id:
#             return Response({'error': 'Student ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        
#         try:
#             student = Student.objects.get(studentid=student_id)
#         except Student.DoesNotExist:
#             return Response({'error': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)
        
#         parent_serializer = ParentSerializer(data=request.data)
#         if parent_serializer.is_valid():
#             parent = parent_serializer.save()
#             StudentParent.objects.create(student=student, parent=parent)
#             return Response({'message': 'Parent information saved and linked successfully'}, status=status.HTTP_201_CREATED)
        
#         return Response(parent_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    
#     def get(self, request, student_id, format=None):
#         try:
#             student = Student.objects.get(studentid=student_id)
#         except Student.DoesNotExist:
#             return Response({'error': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)
        
#         parents = Parent.objects.filter(studentparent__student=student)
        
#         if not parents.exists():
#             return Response({'error': 'No parent information found for this student'}, status=status.HTTP_404_NOT_FOUND)
        
#         parent_serializer = ParentSerializer(parents, many=True)
#         return Response(parent_serializer.data, status=status.HTTP_200_OK)

#     def patch(self, request, student_id, format=None):
#         try:
#             student = Student.objects.get(studentid=student_id)
#         except Student.DoesNotExist:
#             return Response({'error': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)
        
#         parents = Parent.objects.filter(studentparent__student=student)
        
#         if not parents.exists():
#             return Response({'error': 'No parent information found for this student'}, status=status.HTTP_404_NOT_FOUND)
        
#         updated_parents = []
#         for parent in parents:
#             serializer = ParentSerializer(parent, data=request.data, partial=True)
#             if serializer.is_valid():
#                 serializer.save()
#                 updated_parents.append(serializer.data)
#             else:
#                 return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
#         return Response(updated_parents, status=status.HTTP_200_OK)
 

class ParentInformationView(APIView):

    # def post(self, request, student_id, format=None):
    #     if not student_id:
    #         return Response({'error': 'Student ID is required'}, status=status.HTTP_400_BAD_REQUEST)

    #     try:
    #         student = Student.objects.get(studentid=student_id)
    #     except Student.DoesNotExist:
    #         return Response({'error': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)

    #     parent_serializer = ParentSerializer(data=request.data)
    #     if parent_serializer.is_valid():
    #         parent = parent_serializer.save()
    #         StudentParent.objects.create(student=student, parent=parent)
    #         return Response({'message': 'Parent information saved and linked successfully'}, status=status.HTTP_201_CREATED)

    #     return Response(parent_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    def post(self, request, student_id, format=None):
        if not student_id:
            return Response({'error': 'Student ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            student = Student.objects.get(studentid=student_id)
        except Student.DoesNotExist:
            return Response({'error': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)

        parent_serializer = ParentSerializer(data=request.data)

        if parent_serializer.is_valid():
            parent_data = parent_serializer.validated_data

            # Find the parent linked to this student, if it exists
            parents = Parent.objects.filter(studentparent__student=student)

            if parents.exists():
                # Update the existing parent(s) information
                for parent in parents:
                    parent_serializer = ParentSerializer(parent, data=request.data, partial=True)
                    if parent_serializer.is_valid():
                        parent_serializer.save()
                return Response({'message': 'Parent information updated successfully'}, status=status.HTTP_200_OK)

            else:
                # If no parent exists, create a new one
                parent = parent_serializer.save()
                StudentParent.objects.create(student=student, parent=parent)
                return Response({'message': 'Parent information saved and linked successfully'}, status=status.HTTP_201_CREATED)

        return Response(parent_serializer.errors, status=status.HTTP_400_BAD_REQUEST)



    

    def get(self, request, student_id, format=None):
        try:
            student = Student.objects.get(studentid=student_id)
        except Student.DoesNotExist:
            return Response({'error': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)

        parents = Parent.objects.filter(studentparent__student=student)

        if not parents.exists():
            return Response({'error': 'No parent information found for this student'}, status=status.HTTP_404_NOT_FOUND)

        parent_serializer = ParentSerializer(parents, many=True)
        return Response(parent_serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, student_id, format=None):
        try:
            student = Student.objects.get(studentid=student_id)
        except Student.DoesNotExist:
            return Response({'error': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)

        parents = Parent.objects.filter(studentparent__student=student)

        if not parents.exists():
            return Response({'error': 'No parent information found for this student'}, status=status.HTTP_404_NOT_FOUND)

        updated_parents = []
        for parent in parents:
            serializer = ParentSerializer(parent, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                updated_parents.append(serializer.data)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response(updated_parents, status=status.HTTP_200_OK)

            
    

class EditStudentDetailsView(APIView):
    permission_classes = [IsAuthenticated,StudentPermission]
    def post(self, request):
        user = request.user
        try:
            student = Student.objects.get(user=user.id)
            
        except Student.DoesNotExist:
            return Response({'error': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = StudentUpdateSerializer(student, data=request.data, partial=True)
        if serializer.is_valid():
            requested_user_pk = user.id
            studentdata = {field: value for field, value in serializer.validated_data.items()}

            existing_request = Adminrequest.objects.filter(requested_user=requested_user_pk, student=student.studentid, status='pending').first()

            if existing_request:
                existing_request.data = studentdata
                existing_request.save()
                return Response({'status': 'Edit details request updated and pending admin approval'}, status=status.HTTP_200_OK)
            else:
                request_data = {
                    'requested_user': requested_user_pk,
                    'student': student.studentid,
                    'purpose': 'edit_details',
                    'data': studentdata,
                    'status': 'pending'
                }
                request_serializer = AdminrequestSerializer(data=request_data)
                if request_serializer.is_valid():
                    request_serializer.save()
                    return Response({'status': 'Edit details request created and pending admin approval'}, status=status.HTTP_200_OK)
                return Response(request_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# class ParentInformationView(APIView):
#     permission_classes=[IsAuthenticated]
#     def get(self, request, pk):
#         try:
#             student = Student.objects.get(pk=pk)
#         except Student.DoesNotExist:
#             return Response({'error': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)
        
#         parents = Parent.objects.filter(student=student)
        
#         if not parents.exists():
#             return Response({'error': 'Parent information not found'}, status=status.HTTP_404_NOT_FOUND)
        
#         parent_serializer = ParentSerializer(parents, many=True) 
#         return Response(parent_serializer.data, status=status.HTTP_200_OK)
    


class UpdatePhotoRequestView(APIView):
    permission_classes = [IsAuthenticated]



    def get(self, request, student_id):
        try:
            student = Student.objects.get(studentid=student_id)
        except Student.DoesNotExist:
            return Response({'error': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)
        
        photo_id = student.photo_id

        if not photo_id:
            return Response({'error': 'No photo found for this student'}, status=status.HTTP_404_NOT_FOUND)
        
        try:
            photo_data = retrieve_photo(photo_id)
            return Response({'photo': photo_data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request, student_id):
        user = request.user

        try:
            
            student = Student.objects.get(studentid=student_id)
        except Student.DoesNotExist:
            
            return Response({'error': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)
        
        try:
          
            photo_file = request.FILES['photo']
        except KeyError:
            return Response({'error': 'Photo file not found'}, status=status.HTTP_400_BAD_REQUEST)
        
      
        if not isinstance(photo_file, InMemoryUploadedFile):
            return Response({'error': 'Invalid photo file type'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            
            photo_id = handle_photo_upload(student.studentid, photo_file)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

       
        student.photo_id = photo_id
        student.save()

        return Response({'status': 'Photo updated successfully'}, status=status.HTTP_200_OK)




class GenerateIDCardRequestView(APIView):
    permission_classes = [IsAuthenticated,StudentPermission]

    def post(self, request):
        user = request.user
        
        try:
            student = Student.objects.get(user=user)
            
        except Student.DoesNotExist:
            return Response({'error': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)
        try:
            photo_data = retrieve_photo(ObjectId(student.photo_id)) 
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        id_card_info = {
            'first_name': student.fname,
            'surname': student.lname,
            'student_id': student.studentid,
            'date_of_birth': student.dob.strftime('%Y-%m-%d') if student.dob else None,  # Convert date_of_birth to string
            'gender': student.gender,
            'class_and_sec': student.clssectionid.sectionname if student.clssectionid else None,
            'photo': photo_data 
        }

        request_obj = Adminrequest.objects.create(
            requested_user=user,
            student=student,
            purpose='generate_id_card',
            data=id_card_info,
            status='pending'  
        )

        return Response({'status': 'ID card generation request created', 'request_id': request_obj.id}, status=status.HTTP_201_CREATED)


    
    
    
    

class ApproveRequestView(APIView):
    permission_classes = [IsAuthenticated, AdminPermission]
    
    def get(self, request, pk=None):
        if pk:
            try:
                req = Adminrequest.objects.get(pk=pk)
            except Adminrequest.DoesNotExist:
                return Response({'error': 'Request not found'}, status=status.HTTP_404_NOT_FOUND)
            
            
            req_serializer = AdminrequestSerializer(req)
            
          
            student_serializer = StudentSerializer(req.student)
            
            return Response({
                'request_data': req_serializer.data,
                'student_data': student_serializer.data
            }, status=status.HTTP_200_OK)
        else:
            requests = Adminrequest.objects.filter(status="pending")
            serializer = AdminrequestlistSerializer(requests, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, pk):
        try:
            req = Adminrequest.objects.get(pk=pk)
        except Adminrequest.DoesNotExist:
            return Response({'error': 'Request not found'}, status=status.HTTP_404_NOT_FOUND)

        if req.status != 'pending':
            return Response({'status': 'Request already processed'}, status=status.HTTP_400_BAD_REQUEST)

        if req.purpose == 'edit_details':
            student = req.student
            old_data = StudentSerializer(student).data
            new_data = req.data

            serializer = StudentSerializer(student, data=new_data, partial=True)
            if serializer.is_valid():
                serializer.save()
                req.status = 'approved'
                req.approved_time = timezone.now()
                req.save()
                return Response({
                    'status': 'Request approved',
                    'old_data': old_data,
                    'new_data': serializer.data
                }, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        elif req.purpose == 'generate_id_card':
            student = req.student
            id_card_data = req.data

            student.fname = id_card_data.get('first_name', student.fname)
            student.lname = id_card_data.get('surname', student.lname)
            student.dob = id_card_data.get('date_of_birth', student.dob)
            student.gender = id_card_data.get('gender', student.gender)
            student.clssectionid = id_card_data.get('class_and_sec', student.clssectionid)
            student.save()

            req.status = 'approved'
            req.approved_time = timezone.now()
            req.save()

            return Response({
                'status': 'Generate ID card request approved',
                'updated_data': {
                    'first_name': student.fname,
                    'surname': student.lname,
                    'date_of_birth': student.dob,
                    'gender': student.gender,
                    'class_and_sec': student.clssectionid.sectionname,
                    'photo': student.photo 
                }
            }, status=status.HTTP_200_OK)

        return Response({'error': 'Invalid request purpose'}, status=status.HTTP_400_BAD_REQUEST)

class RejectRequestView(APIView):
    permission_classes=[IsAuthenticated,AdminPermission]
    def post(self, request, pk):
        try:
            req = Adminrequest.objects.get(pk=pk)
        except Adminrequest.DoesNotExist:
            return Response({'error': 'Request not found'}, status=status.HTTP_404_NOT_FOUND)

        if req.status != 'pending':
            return Response({'status': 'Request already processed'}, status=status.HTTP_400_BAD_REQUEST)

        req.status = 'rejected'
        req.approved_time = timezone.now()
        req.save()

        return Response({'status': 'Request rejected'}, status=status.HTTP_200_OK)
    





class StudentHomepageView(APIView):
    permission_classes=[IsAuthenticated]
    def get(self, request, pk):
        try:
            student = Student.objects.get(pk=pk)
        except Student.DoesNotExist:
            return Response({'error': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)

        student_data = StudentSerializer(student).data
        welcome_note = f"Welcome {student.fname} to your dashboard!"

        response_data = {
            'student': student_data,
            'welcome_note': welcome_note
        }

        return Response(response_data, status=status.HTTP_200_OK)

class TaskUpdateView(APIView):
    permission_classes=[IsAuthenticated]
    def post(self, request, pk):
        try:
            task = Task.objects.get(pk=pk)
        except Task.DoesNotExist:
            return Response({'error': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)

        task.task_description = request.data.get('task_description', task.task_description)
        task.is_completed = request.data.get('is_completed', task.is_completed)
        task.save()

        return Response({'status': 'Task updated successfully'}, status=status.HTTP_200_OK)

class TaskDeleteView(APIView):
    permission_classes=[IsAuthenticated]
    def delete(self, request, pk):
        try:
            task = Task.objects.get(pk=pk)
        except Task.DoesNotExist:
            return Response({'error': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)

        task.delete()
        return Response({'status': 'Task deleted successfully'}, status=status.HTTP_200_OK)

class TaskCreateView(APIView):
    permission_classes=[IsAuthenticated]
    def post(self, request, pk):
        try:
            student = Student.objects.get(pk=pk)
        except Student.DoesNotExist:
            return Response({'error': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)

        task_description = request.data.get('task_description')
        is_mandatory = request.data.get('is_mandatory', False)

        task = Task.objects.create(
            
            student=student,
            task_description=task_description,
            is_mandatory=is_mandatory
        )

        return Response(TaskSerializer(task).data, status=status.HTTP_201_CREATED)
    

class MonthWiseAttendanceView(APIView):
    permission_classes=[IsAuthenticated]
    def get(self, request, student_id, month):
        try:
            student = Student.objects.get(pk=student_id)
          
            user = student.user
        except Student.DoesNotExist:
            return Response({"error": "Student not found."}, status=status.HTTP_404_NOT_FOUND)

  
        month_wise_data = Attendance.objects.filter(user_type=user, date__month=month).annotate(
            year=ExtractYear('date'),
            month=ExtractMonth('date')
        ).values('year', 'month').annotate(
            present=Count('status', filter=Q(status='Present')),
            absent=Count('status', filter=Q(status='Absent')),
            late=Count('status', filter=Q(status='Late to school'))
        ).order_by('year', 'month')

        return Response(month_wise_data, status=status.HTTP_200_OK)



class LeaveApplicationView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None, format=None):
        user = request.user
        try:
            if pk is None:
                if user.user_type == 'teacher':
                    leave_data = LeaveApplication.objects.filter(status="NotSeen")
                elif user.user_type == 'parent':
                    parent_detail = Parent.objects.get(user=user)
                    student_detail = parent_detail.student
                    leave_data = LeaveApplication.objects.filter(user=student_detail).exclude(status="NotSeen")
                else:
                    leave_data = LeaveApplication.objects.filter(user=user)
                
                user_dict = {leave.leave_id: leave.user.email for leave in leave_data}
                return Response({'msg': user_dict}, status=status.HTTP_200_OK)
            else:
                leave_data = LeaveApplication.objects.get(leave_id=pk)
                
                if user.user_type == 'teacher' and leave_data.status == "NotSeen":
                    leave_data.status = "Seen"
                    leave_data.save()
                    
                
                    student = leave_data.user
                    Notification.objects.create(
                        user=student,  
                        leave_application=leave_data,
                        message=f"Your leave application {leave_data.leave_id} has been viewed by the teacher."
                    )
                
                elif user.user_type == 'parent' and leave_data.user == Parent.objects.get(user=user).student:
                    pass

                serializer = LeaveApplicationRetrieveSerializer(leave_data)
                return Response({'msg': serializer.data}, status=status.HTTP_200_OK)
        except LeaveApplication.DoesNotExist:
            return Response({'msg': 'Leave application does not exist.'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'msg': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, format=None):
        user = request.user
        try:
            serializer = LeaveApplicationSerializer(data=request.data, context={'request': request})
            if serializer.is_valid():
                leave_instance = serializer.save(user=user, status="NotSeen")
                return Response({'msg': 'Leave applied successfully.'}, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'msg': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk, format=None):
        user = request.user
        try:
            leave_data = LeaveApplication.objects.get(leave_id=pk) 

           
            if user.user_type == 'teacher' and leave_data.status == "NotSeen":
                serializer = LeaveApplicationSerializer(leave_data, data=request.data, context={'request': request}, partial=True)
                if serializer.is_valid():
                    leave_instance = serializer.save()
                
                    new_status = request.data.get('status')

               
                    Notification.objects.create(
                        user=leave_data.user,  
                        leave_application=leave_data,
                        message=f"Your leave application {leave_data.id} has been {new_status}.",
                        action=new_status
                    )
                    
                    return Response({'msg': 'Leave application updated successfully.'}, status=status.HTTP_200_OK)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'msg': 'Unauthorized to update leave application'}, status=status.HTTP_403_FORBIDDEN)
        except LeaveApplication.DoesNotExist:
            return Response({'msg': 'Leave application does not exist.'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'msg': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        

class NotificationView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        user = request.user
        notifications = Notification.objects.filter(user=user).order_by('-created_at')
        serializer = NotificationSerializer(notifications, many=True)
        return Response({'notifications': serializer.data}, status=status.HTTP_200_OK)
        
class AttendanceReportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        current_year = now().year


      
        school_days_so_far = Attendance.objects.filter(user=user, date__year=current_year).count()

        days_present = Attendance.objects.filter(user=user, date__year=current_year, status='Present').count()

       
        days_absent = Attendance.objects.filter(user=user, date__year=current_year, status='Absent').count()

       
        vacation_days = LeaveApplication.objects.filter(user=user, leave_type='CL', status="Approved").count()
        sick_days = LeaveApplication.objects.filter(user=user, leave_type='SL', status="Approved").count()
        other_days = LeaveApplication.objects.filter(user=user, leave_type='STL',status="Approved").count()

        report_data = {
            
            'school_days_so_far': school_days_so_far,
            'days_present': days_present,
            'days_absent': days_absent,
            'vacation_days': vacation_days,
            'sick_days': sick_days,
            'other_days': other_days,
        }

        serializer = AttendanceReportSerializer(report_data)
        return Response(serializer.data)
class HolidaysListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        holidays = Holiday.objects.all()
        serializer = HolidaySerializer(holidays, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = HolidaySerializer(data=request.data, many=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class AttendanceListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.is_superuser:
            attendance = Attendance.objects.all()
        else:
            attendance = Attendance.objects.filter(user=user)

        serializer = AttendanceSerializer(attendance, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = AttendanceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AttendanceDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return Attendance.objects.get(pk=pk)
        except Attendance.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        attendance = self.get_object(pk)
        serializer = AttendanceSerializer(attendance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        attendance = self.get_object(pk)
        serializer = AttendanceSerializer(attendance, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        attendance = self.get_object(pk)
        attendance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    

class UploadDocumentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, student_id):
        student = get_object_or_404(Student, pk=student_id)

        if 'document_name' not in request.POST or 'file_path' not in request.FILES:
            return Response({'error': 'Both document_name and file_path are required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        document_file = request.FILES['file_path']

        try:
            # ++Upload document to MongoDB
            document_id = upload_document(student.studentid, document_file)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({'status': 'Document uploaded', 'document_id': document_id}, status=status.HTTP_201_CREATED)
class DownloadDocumentListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, student_id):
        student = get_object_or_404(Student, pk=student_id)
        
        try:
            #++ Retrieve documents from the last 3 months
            documents = get_recent_documents(student.studentid)
            if documents:
                return Response({'documents': documents}, status=status.HTTP_200_OK)
            return Response({"detail": "No recent documents found for the student."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ClassTeacherView(APIView):
    permission_classes = [IsAuthenticated]


    def post(self, request):
        serializer = ClassTeacherSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, pk=None):
        if pk:
            try:
                class_teacher = ClassTeacher.objects.get(pk=pk)
                serializer = ClassTeacherSerializer(class_teacher)
                return Response(serializer.data)
            except ClassTeacher.DoesNotExist:
                return Response({'error': 'Class Teacher not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            class_teachers = ClassTeacher.objects.all()
            serializer = ClassTeacherSerializer(class_teachers, many=True)
            return Response(serializer.data)

    def patch(self, request, pk):
        try:
            class_teacher = ClassTeacher.objects.get(pk=pk)
            serializer = ClassTeacherSerializer(class_teacher, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except ClassTeacher.DoesNotExist:
            return Response({'error': 'Class Teacher not found'}, status=status.HTTP_404_NOT_FOUND)