

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from academics.models import Period
from employees.models import Employee
from students.models import Notification,ClassTeacher,Class,Student,Section
from academics.serializers import PeriodSerializer
from students.serializers import ClassTeacherSerializer,ClassSerializer,SectionSerializer
from user.custom_auth import TeacherPermission
from user.models import User
from rest_framework import status
from django.shortcuts import get_object_or_404
from students.models import Attendance
from user.custom_auth import AdminPermission

class TeacherDashboardView(APIView):
    permission_classes = [TeacherPermission]

    def get(self, request, format=None):
        teacher_user = request.user
        today = timezone.now().date()

        
        try:
            teacher = Employee.objects.get(user=teacher_user)
        except Employee.DoesNotExist:
            return Response({'detail': 'Teacher profile not found.'}, status=404)

       
        timetable = Period.objects.filter(teacherid=teacher, day=today.strftime("%A"))
        timetable_serializer = PeriodSerializer(timetable, many=True)

        notifications = Notification.objects.filter(user=teacher_user)
        notifications_data = []
        for notification in notifications:
            notifications_data.append({
                'message': notification.message,
                'action': notification.action,
                'leave_application_id': notification.leave_application.id if notification.leave_application else None,
            })

        data = {
            'welcome_note': f"welcome {teacher.tfname}!",
            'timetable': timetable_serializer.data,
            'notifications': notifications_data,
        }

        return Response(data, status=200)
    

class TeacherMyClassesView(APIView):
    permission_classes = [IsAuthenticated,TeacherPermission]
    def get(self, request):
        try:
            teacher = request.user. teacher
            # print(teacher) # Assuming the request user is a teacher
            class_teacher = ClassTeacher.objects.filter(teacher=teacher)
            sections = Section.objects.filter(clssectionid__in=class_teacher.values_list('classsec_id', flat=True).distinct())
            classes = Class.objects.filter(classid__in=sections.values_list('classid', flat=True).distinct())
            serializer = ClassSerializer(classes, many=True)
            
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Employee.DoesNotExist:
            return Response({'error': 'Teacher not found'}, status=status.HTTP_404_NOT_FOUND)




class ClassTeacherPageView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request,class_id=None):
        try:
            teacher = get_object_or_404(Employee, user=request.user)
            class_teacher = get_object_or_404(ClassTeacher, teacher=teacher, classsec__classid=class_id)
            sections = Section.objects.filter(clssectionid=class_teacher.classsec_id)
            class_teacher_serializer = ClassTeacherSerializer(class_teacher)
            sections_serializer = SectionSerializer(sections, many=True)
            return Response({
                'class_teacher': class_teacher_serializer.data,
                'sections': sections_serializer.data
            }, status=status.HTTP_200_OK)
        except ClassTeacher.DoesNotExist:
            return Response({'error': 'Class Teacher not found'}, status=status.HTTP_404_NOT_FOUND)


class GetStudentsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, section_id):
        academic_year = request.query_params.get('academic_year', None) 
        # Use clssectionid instead of id
        try:
            section = Section.objects.get(clssectionid=section_id)
        except Section.DoesNotExist:
            return Response({'error': 'Section not found'}, status=404)

        # Fetch students for the section
        students = Student.objects.filter(clssectionid=section)


        if academic_year:  # If academic_year is provided, filter by that as well
            students = students.filter(academic_year=academic_year)
        student_data = [
            {
                'id': student.user.id,
                'name': f"{student.fname} {student.lname}",
                'academic_year': student.academic_year 
            } for student in students
        ]

        return Response({'students': student_data, 'date': timezone.now().date()}, status=200)
    



class SubmitAttendanceView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data
        section_id = data.get('class_section')
        date = data.get('date')
        attendance_records = data.get('attendance')  

       
        if attendance_records is None or not isinstance(attendance_records, list):
            return Response({'error': 'Invalid or missing attendance data.'}, status=400)

        for record in attendance_records:
            custom_student_id = record.get('student_id') 
            status = record.get('status')
            remarks = record.get('remarks', '')

            if custom_student_id is None or status is None:
                return Response({'error': 'Missing student_id or status in attendance record.'}, status=400)

          
            try:
                student = Student.objects.get(studentid=custom_student_id)  
            except Student.DoesNotExist:
                return Response({'error': f'Student with ID {custom_student_id} not found.'}, status=404)

            Attendance.objects.update_or_create(
                user=student.user, 
                class_section_id=section_id,
                date=date,
                defaults={'status': status, 'remarks': remarks}
            )

        return Response({'msg': 'Attendance marked successfully!'}, status=200)

    



class AttendanceHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, section_id):
        date = request.query_params.get('date', None)

    
        attendances = Attendance.objects.filter(class_section_id=section_id, date=date)
        
       
        total_classes = Attendance.objects.filter(class_section_id=section_id).count()
        attendance_data = []
        for attendance in attendances:
            student_name = f"{attendance.user.fname} {attendance.user.lname}"
            status = attendance.status
            remarks = attendance.remarks or "No remarks"

            
            present_days = Attendance.objects.filter(user=attendance.user, status='present', class_section_id=section_id).count()

            
            attendance_percentage = (present_days / total_classes * 100) if total_classes > 0 else 0

            attendance_data.append({
                'name': student_name,
                'status': status,
                'remarks': remarks,
                'date': attendance.date,
                'attendance_percentage': attendance_percentage,
            })

        return Response({'attendance': attendance_data}, status=200)


from students.models import MedicalInfo, EmergencyContact, Student
from students.serializers import MedicalInfoSerializer, EmergencyContactSerializer


class CreateOrUpdateMedicalInfoView(APIView):
    permission_classes = [IsAuthenticated]  # Assuming you handle teacher permissions elsewhere

    def post(self, request, student_id):
        try:
            student = Student.objects.get(studentid=student_id)
            serializer = MedicalInfoSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(student=student)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Student.DoesNotExist:
            return Response({'error': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)
        
    
    def get(self, request, student_id):
        try:
            student = Student.objects.get(studentid=student_id)
            medical_info = MedicalInfo.objects.get(student=student)
            serializer = MedicalInfoSerializer(medical_info)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Student.DoesNotExist:
            return Response({'error': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)
        except MedicalInfo.DoesNotExist:
            return Response({'error': 'Medical information not found'}, status=status.HTTP_404_NOT_FOUND)
        

    def patch(self, request, student_id):
            try:
                student = Student.objects.get(studentid=student_id)
                medical_info = MedicalInfo.objects.get(student=student)  # Retrieve the existing record
                serializer = MedicalInfoSerializer(medical_info, data=request.data, partial=True)  # partial=True for updates
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_200_OK)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            except Student.DoesNotExist:
                return Response({'error': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)
            except MedicalInfo.DoesNotExist:
                return Response({'error': 'Medical information not found'}, status=status.HTTP_404_NOT_FOUND)
        
    

class CreateOrUpdateEmergencyContactView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, student_id):
        try:
            student = Student.objects.get(studentid=student_id)
            serializer = EmergencyContactSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(student=student)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Student.DoesNotExist:
            return Response({'error': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)
        

        
        
    def get(self, request, student_id):
        try:
            student = Student.objects.get(studentid=student_id)
            emergency_contacts = EmergencyContact.objects.filter(student=student)
            serializer = EmergencyContactSerializer(emergency_contacts, many=True)  # multiple contacts
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Student.DoesNotExist:
            return Response({'error': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)
        except EmergencyContact.DoesNotExist:
            return Response({'error': 'Emergency contact not found'}, status=status.HTTP_404_NOT_FOUND)
        


    def patch(self, request, student_id):
        try:
            student = Student.objects.get(studentid=student_id)
            emergency_contact = EmergencyContact.objects.get(student=student)  # Get the specific contact
            serializer = EmergencyContactSerializer(emergency_contact, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Student.DoesNotExist:
            return Response({'error': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)
        except EmergencyContact.DoesNotExist:
            return Response({'error': 'Emergency contact not found'}, status=status.HTTP_404_NOT_FOUND)
        
    



        
# class TeacherProfileView(APIView):
#     permission_classes=[IsAuthenticated]
#     def get(self, request, pk=None):
#         try:
#             if pk:
#                 student = Employee.objects.get(pk=pk)
#                 serializer = EmployeeSerializer(Employee) 
#             else:
#                student = Employee.objects.all()
#                serializer=EmployeeSerializer(student,many=True)
#             return Response(serializer.data)
#         except Employee.DoesNotExist:
#             return Response({'error': 'Employee not found'}, status=status.HTTP_404_NOT_FOUND)
#         except Exception as e:
#             return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

from students.serializers import EmployeeDetailSerializer,EmployeeListSerializer
# class EmployeeView(APIView):
#     # permission_classes = [IsAuthenticated, AdminPermission]

#     def get(self, request, pk=None):
#         if pk: 
#             # year_of_joining = request.query_params.get('year_of_joining')  # If a primary key is provided, return the specific employee
#             try:
#                 employee = Employee.objects.get(pk=pk)
#                 serializer = EmployeeDetailSerializer(employee)
#                 return Response(serializer.data)
#             except Employee.DoesNotExist:
#                 return Response({'error': 'Employee not found'}, status=status.HTTP_404_NOT_FOUND)
#         else:  # Return the list of all employees if no pk is provided
#             employees = Employee.objects.all()

#             # if year_of_joining:  # Filter by year_of_joining if provided
#             #     employees = employees.filter(date_of_joining__year=year_of_joining)

#             serializer = EmployeeDetailSerializer(employees, many=True)
#             return Response(serializer.data)
# class EmployeeView(APIView):
#     # permission_classes = [IsAuthenticated, AdminPermission]

#     def get(self, request, pk=None):
#         # Get the year of joining from query params
#         year_of_joining = request.query_params.get('year_of_joining', None)

#         if pk:
#             try:
#                 employee = Employee.objects.get(pk=pk)
#                 serializer = EmployeeDetailSerializer(employee)
#                 return Response(serializer.data)
#             except Employee.DoesNotExist:
#                 return Response({'error': 'Employee not found'}, status=status.HTTP_404_NOT_FOUND)
#         else:  # Return the list of all employees if no pk is provided
#             employees = Employee.objects.all()

#             # Filter by year_of_joining if provided
#             if year_of_joining:
#                 employees = employees.filter(date_of_joining__year=year_of_joining)

#             # Order employees by name
#             employees = employees.order_by('user__fname')  # Assuming 'user' has a field 'fname'

#             serializer = EmployeeDetailSerializer(employees, many=True)
#             return Response(serializer.data)

#     def post(self, request):
#         serializer = EmployeeDetailSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


#     def patch(self, request, pk):
#         try:
#             employee = Employee.objects.get(pk=pk)
#         except Employee.DoesNotExist:
#             return Response({'error': 'Employee not found'}, status=status.HTTP_404_NOT_FOUND)

#         serializer = EmployeeDetailSerializer(employee, data=request.data, partial=True)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_200_OK)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class EmployeeView(APIView):
    # permission_classes = [IsAuthenticated, AdminPermission]

    def get(self, request, pk=None):
        year_of_joining = request.query_params.get('year_of_joining', None)

        if pk:
            try:
                employee = Employee.objects.get(pk=pk)
                serializer = EmployeeDetailSerializer(employee)
                return Response(serializer.data)
            except Employee.DoesNotExist:
                return Response({'error': 'Employee not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            employees = Employee.objects.all()
            if year_of_joining:
                employees = employees.filter(date_of_joining__year=year_of_joining)
            employees = employees.order_by('fname')
            serializer = EmployeeListSerializer(employees, many=True)
            return Response(serializer.data)
        
    
    def post(self, request):
        serializer = EmployeeDetailSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        try:
            employee = Employee.objects.get(pk=pk)
        except Employee.DoesNotExist:
            return Response({'error': 'Employee not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = EmployeeDetailSerializer(employee, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



    

from students.serializers import SubjectTeacherSerializer
from academics.models import SubjectTeacher,Subject
class AdminEmployeeClassesView(APIView):
    # permission_classes = [IsAuthenticated, AdminPermission]  # Use Admin permission instead of TeacherPermission

    def get(self, request):
        try:
            # Get all teachers
            teachers = Employee.objects.all()  # Get all employees (teachers)
            
            # Prepare data to hold the classes and subjects for each teacher
            teacher_data = []
            
            for teacher in teachers:
                # Get all subjects the teacher is teaching
                subject_teachers = SubjectTeacher.objects.filter(teacherid=teacher)
                
                # Get the related subjects and classes
                subjects = Subject.objects.filter(subjectid__in=subject_teachers.values_list('subjectid', flat=True))
                classes = Class.objects.filter(classid__in=subjects.values_list('classid', flat=True).distinct())
                
                # Prepare the response with the classes, subjects, and teacher information
                class_data = []
                for cls in classes:
                    sections = Section.objects.filter(classid=cls.classid)
                    for section in sections:
                        # Get the subjects for each section and map the teacher's information
                        mapping = {
                            'class_section': f"{cls.classname}{section.sectionname}",
                            'subjects': []
                        }
                        for subject_teacher in subject_teachers.filter(subjectid__in=subjects, teacherid=teacher):
                            subject = subject_teacher.subjectid
                            mapping['subjects'].append({
                                'teacher_code': teacher.empid,
                                'teacher_name': f"{teacher.fname} {teacher.lname}",
                                'subject': subject.subjectname
                            })
                        class_data.append(mapping)
                
                # Append the teacher's data with their assigned classes and subjects
                teacher_data.append({
                    'teacher_id': teacher.empid,
                    'teacher_name': f"{teacher.fname} {teacher.lname}",
                    'classes': class_data
                })

            # Return the teacher data
            return Response(teacher_data, status=status.HTTP_200_OK)

        except Employee.DoesNotExist:
            return Response({'error': 'Teacher not found'}, status=status.HTTP_404_NOT_FOUND)
        




# class AssignSubjectTeachersView(APIView):
#     def get(self, request, class_id):
#         try:
#             # Fetch subjects for the selected class
#             subjects = Subject.objects.filter(classid=class_id)
#             subject_list = [{"id": subject.subjectid, "name": subject.subjectname} for subject in subjects]

#             # Fetch teachers based on subject preferences for the subjects in the selected class
#             subject_teachers = SubjectTeacher.objects.filter(subjectid__in=subjects)
#             teacher_ids = subject_teachers.values_list('teacherid', flat=True).distinct()
#             teachers = Employee.objects.filter(empid__in=teacher_ids)  # Assuming empid is the primary key

#             teacher_list = [{"id": teacher.empid, "name": f"{teacher.fname} {teacher.lname}"} for teacher in teachers]

#             return Response({
#                 "subjects": subject_list,
#                 "teachers": teacher_list
#             }, status=status.HTTP_200_OK)

#         except Subject.DoesNotExist:
#             return Response({"error": "Subjects not found for this class"}, status=status.HTTP_404_NOT_FOUND)

#         except Employee.DoesNotExist:
#             return Response({"error": "No teachers found"}, status=status.HTTP_404_NOT_FOUND)



#     def post(self, request):
#         try:
#             class_id = request.data.get('class_id')
#             subject_id = request.data.get('subject_id')
#             teacher_ids = request.data.get('teacher_ids')  # list of teacher IDs

#             if not subject_id or not class_id or not teacher_ids:
#                 return Response({"error": "class_id, subject_id, and teacher_ids are required"}, status=status.HTTP_400_BAD_REQUEST)

#             # Validate that subject exists
#             try:
#                 subject = Subject.objects.get(subjectid=subject_id, classid=class_id)
#             except Subject.DoesNotExist:
#                 return Response({"error": "Subject not found for this class"}, status=status.HTTP_404_NOT_FOUND)

#             # Remove old subject-teacher mappings for this subject
#             SubjectTeacher.objects.filter(subjectid=subject).delete()

#             # Create new subject-teacher mappings
#             for teacher_id in teacher_ids:
#                 try:
#                     teacher = Employee.objects.get(empid=teacher_id)
#                     # Create new entry for teacher and subject in the SubjectTeacher table
#                     SubjectTeacher.objects.create(
#                         teacherid=teacher,
#                         subjectid=subject,
#                     )
#                 except Employee.DoesNotExist:
#                     return Response({"error": f"Teacher with ID {teacher_id} not found"}, status=status.HTTP_404_NOT_FOUND)

#                 return Response({"message": "Teachers assigned successfully"}, status=status.HTTP_201_CREATED)

#         except Exception as e:
#                 return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
from academics.serializers import SubjectSerializer
# class AssignSubjectTeachersView(APIView):
   
#     def get(self, request):
#         # Fetch classid from query parameters
#         class_id = request.query_params.get('classid', None)
#         if not class_id:
#             return Response({"error": "Class ID is required"}, status=status.HTTP_400_BAD_REQUEST)

#         # Attempt to get the corresponding Class instance
#         try:
#             class_instance = Class.objects.get(classid=class_id)
#         except Class.DoesNotExist:
#             return Response({"error": "Invalid Class ID"}, status=status.HTTP_404_NOT_FOUND)

#         # Fetch subjects for the class
#         subjects = Subject.objects.filter(classid=class_instance)
#         subject_serializer = SubjectSerializer(subjects, many=True)

#         # Fetch all available teachers who have subject preferences related to those subjects
#         teachers = Employee.objects.filter(subjectteacher_set__subjectid__in=subjects).distinct()
#         teacher_serializer = EmployeeDetailSerializer(teachers, many=True)

#         assignments = []
#         for subject in subjects:
#             subject_assignments = SubjectTeacher.objects.filter(subjectid=subject)
#             for assignment in subject_assignments:
#                 assignments.append({
#                     "subject": subject.subjectname,
#                     "teacher": assignment.teacherid.fname if assignment.teacherid else None,
#                     "class_id": class_instance.classid,
#                     "teacher_id": assignment.teacherid.empid if assignment.teacherid else None,
#                 })

#         return Response({
#             "subjects": subject_serializer.data,
#             "teachers": teacher_serializer.data,
#             "assignments": assignments,  # Include the assignments in the response
#         }, status=status.HTTP_200_OK)


#         # Assign teacher to a subject
#     def post(self, request):
#         # Assign teacher to a subject
#             subject_teacher_data = request.data.get('subject_teacher')
#             if not subject_teacher_data:
#                 return Response({"error": "Subject and teacher data are required"}, status=status.HTTP_400_BAD_REQUEST)

#             subject_id = subject_teacher_data.get('subjectid')
#             teacher_id = subject_teacher_data.get('teacherid')

#             # Check if subject and teacher exist
#             try:
#                 subject = Subject.objects.get(subjectid=subject_id)
#                 teacher = Employee.objects.get(empid=teacher_id)
#             except (Subject.DoesNotExist, Employee.DoesNotExist):
#                 return Response({"error": "Invalid subject or teacher"}, status=status.HTTP_404_NOT_FOUND)
            

#             teacher_class_count = SubjectTeacher.objects.filter(teacherid=teacher).count()
#             if teacher_class_count >= 4:
#               return Response({"error": "This teacher is already assigned to 4 or more classes."}, status=status.HTTP_400_BAD_REQUEST)

#             # Create or update the subject-teacher relation
#             SubjectTeacher.objects.update_or_create(
#                 subjectid=subject,
#                 teacherid=teacher
#             )

#             return Response({"message": "Teacher assigned to subject successfully"}, status=status.HTTP_200_OK)
    

    


class AssignSubjectTeachersView(APIView):
    # Retrieve subjects and teachers for a class-section
    def get(self, request,classid,sectionid):
            # Retrieve classid and clssectionid from the request body instead of query parameters
            class_id = classid
            clssection_id = sectionid

            if not class_id or not clssection_id:
                return Response({"error": "Both Class ID and Section ID are required"}, status=status.HTTP_400_BAD_REQUEST)


            # Attempt to get the corresponding Class and Section instances
            try:
                class_instance = Class.objects.get(classid=class_id)
                section_instance = Section.objects.get(clssectionid=clssection_id)  # Updated this line
            except Class.DoesNotExist:
                return Response({"error": "Invalid Class ID"}, status=status.HTTP_404_NOT_FOUND)
            except Section.DoesNotExist:
                return Response({"error": "Invalid Section ID"}, status=status.HTTP_404_NOT_FOUND)

            # Fetch subjects for the class
            subjects = Subject.objects.filter(classid=class_instance)
            if not subjects.exists():
                return Response({"error": "No subjects found for the given class"}, status=status.HTTP_404_NOT_FOUND)
            
            subject_serializer = SubjectSerializer(subjects, many=True)

            # Fetch all available teachers who have subject preferences related to those subjects
            teachers = Employee.objects.filter(subjectteacher_set__subjectid__in=subjects).distinct()
            teacher_serializer = EmployeeDetailSerializer(teachers, many=True)

            assignments = []
            for subject in subjects:
                # Fetch assignments using clssectionid instead of sectionid
                subject_assignments = SubjectTeacher.objects.filter(subjectid=subject, clssectionid=section_instance)  
                for assignment in subject_assignments:
                    assignments.append({
                        "subject": subject.subjectname,
                        "teacher": assignment.teacherid.fname if assignment.teacherid else None,
                        "class_id": class_instance.classid,
                        "section_id": section_instance.clssectionid,  # Use clssectionid here
                        "teacher_id": assignment.teacherid.empid if assignment.teacherid else None,
                    })

            return Response({
                "subjects": subject_serializer.data,
                "teachers": teacher_serializer.data,
                "assignments": assignments,  # Include the assignments in the response
            }, status=status.HTTP_200_OK)


    # Assign teacher to a subject for a class-section
    def post(self, request):
        subject_teacher_data = request.data.get('subject_teacher')
        if not subject_teacher_data:
            return Response({"error": "Subject, teacher, class, and section data are required"}, status=status.HTTP_400_BAD_REQUEST)

        subject_id = subject_teacher_data.get('subjectid')
        teacher_id = subject_teacher_data.get('teacherid')
        class_id = subject_teacher_data.get('classid')
        clssection_id = subject_teacher_data.get('sectionid')  # Adjusted to match your payload

        # Check for required fields
        if not subject_id or not teacher_id or not class_id or not clssection_id:
            return Response({"error": "All of Subject ID, Teacher ID, Class ID, and Section ID are required"}, status=status.HTTP_400_BAD_REQUEST)

        # Check if subject, teacher, class, and section exist
        try:
            subject = Subject.objects.get(subjectid=subject_id, classid=class_id)
            teacher = Employee.objects.get(empid=teacher_id)
            section = Section.objects.get(clssectionid=clssection_id)  # Ensure using clssectionid here
        except (Subject.DoesNotExist, Employee.DoesNotExist, Section.DoesNotExist):
            return Response({"error": "Invalid subject, teacher, class, or section"}, status=status.HTTP_404_NOT_FOUND)

        # Check if there is already a teacher assigned to this subject in the same class and section
        existing_assignment = SubjectTeacher.objects.filter(subjectid=subject, clssectionid=section).first()

        if existing_assignment:
            # Update the existing assignment with the new teacher
            existing_assignment.teacherid = teacher
            existing_assignment.save()
            return Response({"message": "Teacher assignment updated successfully"}, status=status.HTTP_200_OK)
        else:
            # If no existing assignment, create a new one
            SubjectTeacher.objects.create(
                subjectid=subject,
                teacherid=teacher,
                clssectionid=section
            )
            return Response({"message": "Teacher assigned to subject successfully"}, status=status.HTTP_200_OK)
