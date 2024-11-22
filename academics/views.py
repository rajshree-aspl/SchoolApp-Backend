from django.shortcuts import render

# Create your views here.
from rest_framework.permissions import IsAuthenticated
from .models import SubjectTeacher

from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import ClassSchedule,Syllabus
from .serializers import ClassScheduleSerializer,SyllabusSerializer,SubjectTeacherSerializer,SubjectSerializer
from django.template.loader import render_to_string
from xhtml2pdf import pisa
from user.models import User

# import weasyprints


from django.http import HttpResponse

class DayTimetableView(APIView):
    def get(self, request, student_id):
        today = timezone.now().date()
        
        # Get today's classes
        classes = ClassSchedule.objects.filter(student_id=student_id, date=today)
        classes_serializer = ClassScheduleSerializer(classes, many=True)

       
        syllabus = Syllabus.objects.filter(subject__in=classes.values_list('subject_id', flat=True))
        syllabus_serializer = SyllabusSerializer(syllabus, many=True)

        return Response({
            'classes': classes_serializer.data,
            'syllabus': syllabus_serializer.data
        })

class WeekTimetableView(APIView):
    def get(self, request, student_id):
        today = timezone.now().date()
        start_of_week = today - timezone.timedelta(days=today.weekday())
        end_of_week = start_of_week + timezone.timedelta(days=6)

        # Fetch classes for the week
        classes = ClassSchedule.objects.filter(
            student_id=student_id,
            date__range=[start_of_week, end_of_week]
        )
        classes_serializer = ClassScheduleSerializer(classes, many=True)
        if 'download' in request.GET:
                # Generate and return PDF
                html = render_to_string('academics/weekly_timetable.html', {'classes': classes_serializer.data})
                response = HttpResponse(content_type='application/pdf')
                response['Content-Disposition'] = 'attachment; filename="weekly_timetable.pdf"'
                pisa_status = pisa.CreatePDF(html, dest=response)
                if pisa_status.err:
                    return HttpResponse('Error generating PDF', status=500)
                return response

         
        return Response({'classes': classes_serializer.data})

class MonthTimetableView(APIView):
    def get(self, request, student_id, month, year):
 
        classes = ClassSchedule.objects.filter(
            student_id=student_id,
            date__year=year,
            date__month=month
        )
        classes_serializer = ClassScheduleSerializer(classes, many=True)

        return Response({
            'classes': classes_serializer.data
        })


class TeacherTimetableView(APIView):
    def get(self, request, teacher_id):
        today = timezone.now().date()
    
        classes = ClassSchedule.objects.filter(teacher__teacherid=teacher_id, date=today)
        classes_serializer = ClassScheduleSerializer(classes, many=True)
        
        return Response({
            'timetable': classes_serializer.data
        })
    





# views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from .models import ClassSchedule, Student, Subject, Class
from .serializers import AttendanceSerializer, ClassScheduleSerializer,SectionSerializer,ClassSerializer
from students.serializers import StudentSerializer

# class CreateSubjectView(APIView):
#     def post(self, request):
#         serializer = SubjectSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     def get(self, request):
#         subjects = Subject.objects.all()
#         serializer = SubjectSerializer(subjects, many=True)
#         return Response(serializer.data)

#     def patch(self, request, pk):
#         try:
#             subject = Subject.objects.get(pk=pk)
#         except Subject.DoesNotExist:
#             return Response({"error": "Subject not found"}, status=status.HTTP_404_NOT_FOUND)

#         serializer = SubjectSerializer(subject, data=request.data, partial=True)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_200_OK)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# class CreateClassView(APIView):
#     def post(self, request):
#         serializer = ClassSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     def get(self, request):
#         classes = Class.objects.all()
#         serializer = ClassSerializer(classes, many=True)
#         return Response(serializer.data)

#     def patch(self, request, pk):
#         try:
#             class_instance = Class.objects.get(pk=pk)
#         except Class.DoesNotExist:
#             return Response({"error": "Class not found"}, status=status.HTTP_404_NOT_FOUND)

#         serializer = ClassSerializer(class_instance, data=request.data, partial=True)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_200_OK)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
from students.models import Section,Attendance,ClassTeacher
# class CreateSectionView(APIView):
#     def post(self, request):
#         serializer = SectionSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
#     def get(self, request):
        
#         sections = Section.objects.all()
#         serializer = SectionSerializer(sections, many=True)
#         return Response(serializer.data)
    
#     def patch(self, request, pk):
#         try:
#             section = Section.objects.get(pk=pk)
#         except Section.DoesNotExist:
#             return Response({"error": "Section not found"}, status=status.HTTP_404_NOT_FOUND)

#         serializer = SectionSerializer(section, data=request.data, partial=True)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_200_OK)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# class MarkAttendanceView(APIView):
#     def post(self, request):
#         attendance_data = request.data  # Expecting a list of records
#         responses = []

#         for record in attendance_data:
#             student_id = record.get('student_id')
#             class_schedule_id = record.get('class_schedule_id')
#             status = record.get('status')
#             remarks = record.get('remarks', '')

#             try:
#                 class_schedule = ClassSchedule.objects.get(id=class_schedule_id)
#                 attendance, created = Attendance.objects.update_or_create(
#                     user_id=student_id,
#                     date=timezone.now().date(),
#                     class_schedule=class_schedule,
#                     defaults={'status': status, 'remarks': remarks}
#                 )
#                 responses.append({
#                     'student_id': student_id,
#                     'status': status,
#                     'created': created
#                 })
#             except ClassSchedule.DoesNotExist:
#                 return Response({"error": f"Class schedule with id {class_schedule_id} does not exist"}, status=status.HTTP_400_BAD_REQUEST)

#         return Response(responses, status=status.HTTP_201_CREATED)

#     def get(self, request):
#         """Retrieve all attendance records."""
#         attendances = Attendance.objects.all()
#         serializer = AttendanceSerializer(attendances, many=True)
#         return Response(serializer.data)

#     def patch(self, request):
#         """Update attendance records."""
#         attendance_data = request.data
#         responses = []

#         for record in attendance_data:
#             student_id = record.get('student_id')
#             class_schedule_id = record.get('class_schedule_id')

#             try:
#                 attendance = Attendance.objects.get(
#                     user_id=student_id,
#                     class_schedule_id=class_schedule_id,
#                     date=timezone.now().date()
#                 )
#                 attendance.status = record.get('status', attendance.status)
#                 attendance.remarks = record.get('remarks', attendance.remarks)
#                 attendance.save()
#                 responses.append({'student_id': student_id, 'updated': True})
#             except Attendance.DoesNotExist:
#                 responses.append({'student_id': student_id, 'updated': False})

#         return Response(responses, status=status.HTTP_200_OK)


# from .serializers import BulkCreateAttendanceSerializer

# class TeacherAttendanceView(APIView):
#     def get(self, request, section_id):
#         # Check if the section exists using clssectionid
#         if not Section.objects.filter(clssectionid=section_id).exists():
#             return Response({"detail": "Section not found."}, status=status.HTTP_404_NOT_FOUND)

#         # Get class schedules for the section using clssectionid
#         class_schedules = ClassSchedule.objects.filter(section__clssectionid=section_id)  # Correctly use section__clssectionid

#         # Now, you can get attendance records based on those class schedules
#         attendances = Attendance.objects.filter(class_schedule__in=class_schedules)

#         # Serialize and return your data
#         serializer = AttendanceSerializer(attendances, many=True)
#         return Response(serializer.data)
    
# from rest_framework.views import APIView
from django.db.models import Count



from employees.models import Employee
class AddClassView(APIView):
    def post(self, request):
        # Serializer for class data
        serializer = ClassSerializer(data=request.data)
        if serializer.is_valid():
            class_instance = serializer.save()

            # Prepare response data to include sections and teacher details
            response_data = serializer.data
            response_data['sections'] = []

            # Process each section and assign the corresponding teacher
            sections_data = request.data.get('sections', [])
            for section_data in sections_data:
                # Create section instance
                section = Section.objects.create(
                    classid=class_instance,
                    sectionname=section_data.get('sectionname')
                )

                # Assign a teacher using the provided email
                teacher_email = section_data.get('teacher')
                try:
                    # Fetch the teacher by email (Employee is linked to User via FK)
                    teacher = Employee.objects.get(user__email=teacher_email)
                    
                    # Create a ClassTeacher instance linking the teacher and section
                    ClassTeacher.objects.create(
                        teacher=teacher,
                        section=section,
                        academicyear=section_data.get('academicyear', '2024-2025')
                    )

                    # Append the section info with the teacher's name to the response
                    teacher_name = f"{teacher.user.fname} {teacher.user.lname}"
                    response_data['sections'].append({
                        "sectionname": section.sectionname,
                        "teacher": teacher_name,  # Single teacher's name (string)
                        "academicyear": section_data.get('academicyear', '2024-2025')
                    })

                except Employee.DoesNotExist:
                    return Response(
                        {"error": f"Teacher with email {teacher_email} does not exist."},
                        status=status.HTTP_400_BAD_REQUEST
                    )

            # Return the response data, including sections and assigned teacher names
            return Response(response_data, status=status.HTTP_201_CREATED)
        
        # Return error if serializer is not valid
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    def get(self, request):
        # Retrieve all classes with student counts
        classes = Class.objects.annotate(num_students=Count('section__student_clssectionid'))

        # Serialize the classes
        serializer = ClassSerializer(classes, many=True)

        # Prepare the response data
        class_list = []
        for class_data, class_instance in zip(serializer.data, classes):
            class_data['num_students'] = class_instance.num_students
            
            # Add sections and class teachers for each class
            class_data['sections'] = []
            for section in class_instance.section.all():  # Access sections through related manager
                # Add section data
                section_data = {
                    'sectionid': section.clssectionid,
                    'sectionname': section.sectionname,
                    'class_teachers': ''  # Initialize as empty string for single teacher
                }
                
                # Access class teachers related to the section
                class_teacher = section.classteacher_classsecid.first()  # Retrieve the first class teacher
                if class_teacher:  # If a teacher is assigned
                    section_data['class_teachers'] = f"{class_teacher.teacher.user.email}"
                
                # Append the section data with the single teacher's email (as string)
                class_data['sections'].append(section_data)

            class_list.append(class_data)

        return Response(class_list, status=200)


    
    def put(self, request, class_id):
        try:
            class_instance = Class.objects.get(classid=class_id)
        except Class.DoesNotExist:
            return Response({"error": "Class not found."}, status=status.HTTP_404_NOT_FOUND)

        # Update the class instance itself
        serializer = ClassSerializer(class_instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()

            # Get or update sections and class teachers
            sections_data = request.data.get('sections', [])
            existing_sections = Section.objects.filter(classid=class_instance)

            for section_data in sections_data:
                # Check if the section already exists
                section_instance, created = Section.objects.update_or_create(
                    classid=class_instance,
                    sectionname=section_data.get('sectionname'),  # Unique by sectionname and classid
                    defaults={
                        'classid': class_instance
                    }
                )

                # Update the teacher for the section
                teacher_email = section_data.get('teacher')  # Ensure consistent key
                if teacher_email:
                    try:
                        teacher = Employee.objects.get(user__email=teacher_email)
                        # Update or create the ClassTeacher entry for this section
                        ClassTeacher.objects.update_or_create(
                            section=section_instance,
                            defaults={
                                'teacher': teacher,
                                'academicyear': section_data.get('academicyear', '2024-2025')
                            }
                        )
                    except Employee.DoesNotExist:
                        return Response({"error": f"Teacher with email {teacher_email} does not exist."}, status=status.HTTP_400_BAD_REQUEST)

            # Remove sections that are no longer in the request
            section_names_in_request = [s['sectionname'] for s in sections_data]
            for section in existing_sections:
                if section.sectionname not in section_names_in_request:
                    section.delete()

            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



        

class AddSubjectView(APIView):
    def post(self, request):
        serializer = SubjectSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get(self, request, pk=None):
        if pk is not None:
          
            try:
                subject = Subject.objects.get(subjectid=pk)
                serializer = SubjectSerializer(subject)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Subject.DoesNotExist:
                return Response({"error": "Subject not found."}, status=status.HTTP_404_NOT_FOUND)

       
        subjects = Subject.objects.all()
        serializer = SubjectSerializer(subjects, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

    def put(self, request, pk):
        try:
            subject_instance = Subject.objects.get(subjectid=pk)
        except Subject.DoesNotExist:
            return Response({"error": "Subject not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = SubjectSerializer(subject_instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TeacherAttendanceIndiviualView(APIView):
    def get(self, request):
        try:
            user_id = request.query_params.get('user_id')  # New parameter to specify a single student
            # Check if filtering by a specific student
            if user_id:
                try:
                    # Filter attendance for a single student if `student_id` is provided
                    # student = students_in_section.get(studentid=student_id)
                    attendance_record = Attendance.objects.filter(user_id=user_id)
                    print('Attendance',attendance_record)
                except:
                    return Response({'error': 'Student not found maybe.'}, status=status.HTTP_404_NOT_FOUND)
            else:
                return Response({'error': 'Student ID required.'}, status=status.HTTP_400_NOT_FOUND)

            if not attendance_record.exists():
                return Response({'error': 'No attendance records found .'}, status=status.HTTP_404_NOT_FOUND)

            # Serialize attendance records
            serializer = AttendanceSerializer(attendance_record, many=True)
            return Response({'attendance_records': serializer.data}, status=status.HTTP_200_OK)

        except:
            return Response({'error': 'error.'}, status=status.HTTP_404_NOT_FOUND)

class TeacherAttendanceView(APIView):
    def post(self, request, section_id):
        # Retrieve the section
        try:
            section = Section.objects.get(clssectionid=section_id)
            students_in_section = Student.objects.filter(clssectionid=section)
        except Section.DoesNotExist:
            return Response({'error': 'Section not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        # Get session type (morning/afternoon) from the request
        session_type = request.data.get('session_type')
        if session_type not in ['morning', 'afternoon']:
            return Response({'error': 'Invalid session type.'}, status=status.HTTP_400_BAD_REQUEST)

        attendance_data = request.data.get('attendances', [])
        responses = []
        valid_attendance_records = []

        for record in attendance_data:
            studentid = record.get('studentid')
            try:
                student = students_in_section.get(studentid=studentid)
                user_id = student.user.id

                attendance_record_data = {
                    'user': user_id,
                    'status': record.get('status'),
                    'remarks': record.get('remarks', ''),
                    'date': timezone.localtime(timezone.now()).date(),  # Set today's date
                    'session_type': session_type  # Add session type to the record
                }
                print(attendance_record_data)
                serializer = AttendanceSerializer(data=attendance_record_data)

                if serializer.is_valid():
                    # Check if attendance already exists for the student, date, and session
                    if Attendance.objects.filter(user_id=user_id, date=attendance_record_data['date'], session_type=session_type).exists():
                        responses.append({
                            'student_id': studentid,
                            
                            'updated': False,
                            'errors': 'Attendance record already exists for this date and session.'
                        })
                    else:
                        attendance_record = serializer.save()
                        valid_attendance_records.append(attendance_record)
                        responses.append({'student_id': studentid, 'updated': True})
                else:
                    responses.append({'student_id': studentid, 'updated': False, 'errors': serializer.errors})

            except Student.DoesNotExist:
                responses.append({'student_id': studentid, 'updated': False, 'errors': 'Student not found.'})

        return Response({
            'responses': responses,
            'total_created': len(valid_attendance_records)
        }, status=status.HTTP_201_CREATED)

  
    def get(self, request, section_id):
        try:
            # Get the section object
            section = Section.objects.get(clssectionid=section_id)
            date = request.query_params.get('date')
            session_type = request.query_params.get('session_type')
            student_id = request.query_params.get('student_id')  # New parameter to specify a single student

            # Ensure all necessary parameters are provided
            if not date or not session_type:
                return Response({'error': 'Both date and session_type parameters are required.'}, status=status.HTTP_400_BAD_REQUEST)

            # Get the students in the section
            students_in_section = Student.objects.filter(clssectionid=section, user__user_type='student')
            
            # Check if filtering by a specific student
            if student_id:
                try:
                    # Filter attendance for a single student if `student_id` is provided
                    student = students_in_section.get(studentid=student_id)
                    attendance_record = Attendance.objects.filter(
                        user=student.user,
                        date=date,
                        session_type=session_type
                    )
                except Student.DoesNotExist:
                    return Response({'error': 'Student not found in this section.'}, status=status.HTTP_404_NOT_FOUND)
            else:
                # Retrieve attendance records for all students in the section if no student_id specified
                attendance_record = Attendance.objects.filter(
                    user__in=students_in_section.values_list('user', flat=True),
                    date=date,
                    session_type=session_type
                )

            if not attendance_record.exists():
                return Response({'error': 'No attendance records found for the specified date and session type.'}, status=status.HTTP_404_NOT_FOUND)

            # Serialize attendance records
            serializer = AttendanceSerializer(attendance_record, many=True)
            return Response({'attendance_records': serializer.data}, status=status.HTTP_200_OK)

        except Section.DoesNotExist:
            return Response({'error': 'Section not found.'}, status=status.HTTP_404_NOT_FOUND)


    def patch(self, request):
        student_id = request.data.get('student_id')
        date = request.data.get('date')
        session_type = request.data.get('session_type')

        if not student_id or not date or not session_type:
            return Response({'error': 'student_id, date, and session_type are required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            student = Student.objects.get(studentid=student_id)
            attendance_record = Attendance.objects.get(
                user=student.user,
                date=date,
                session_type=session_type
            )
        except Student.DoesNotExist:
            return Response({'error': 'Student not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Attendance.DoesNotExist:
            return Response({'error': 'Attendance record not found for the specified date and session type.'}, status=status.HTTP_404_NOT_FOUND)

        # Partial update with the data in the request
        serializer = AttendanceSerializer(attendance_record, data=request.data, partial=True)
        if serializer.is_valid():
            updated_record = serializer.save()
            return Response({'attendance': serializer.data}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




    







class GetStudentsView(APIView):
    def get(self, request, class_id, section_id):
        students = Student.objects.filter(clssectionid=section_id)
        serializer = StudentSerializer(students, many=True)
        return Response(serializer.data)



class SubjectTeacherView(APIView):
    permission_classes = [IsAuthenticated]


    def post(self, request):
        serializer = SubjectTeacherSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, pk=None):
        if pk:
            try:
                subject_teacher = SubjectTeacher.objects.get(pk=pk)
                serializer = SubjectTeacherSerializer(subject_teacher)
                return Response(serializer.data)
            except SubjectTeacher.DoesNotExist:
                return Response({'error': 'Subject Teacher not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            subject_teachers = SubjectTeacher.objects.all()
            serializer = SubjectTeacherSerializer(subject_teachers, many=True)
            return Response(serializer.data)

    def patch(self, request, pk):
        try:
            subject_teacher = SubjectTeacher.objects.get(pk=pk)
            serializer = SubjectTeacherSerializer(subject_teacher, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except SubjectTeacher.DoesNotExist:
            return Response({'error': 'Subject Teacher not found'}, status=status.HTTP_404_NOT_FOUND)
        
from .models import Timetable,AcademicYear
from students.serializers import EmployeeDetailSerializer
from rest_framework.exceptions import ValidationError

class TimetableView(APIView):
    def get(self, request):
        # Fetch class-section, academic year, day, and time from query parameters
        class_id = request.query_params.get('classid', None)
        academic_year_id = request.query_params.get('academic_year', None)
        day = request.query_params.get('day', None)
        time_slot = request.query_params.get('time', None)
        
        if not class_id or not academic_year_id or not day or not time_slot:
            return Response({"error": "Class ID, academic year, day, and time slot are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            class_instance = Class.objects.get(classid=class_id)
            academic_year = AcademicYear.objects.get(id=academic_year_id)
        except (Class.DoesNotExist, AcademicYear.DoesNotExist):
            return Response({"error": "Invalid Class ID or Academic Year"}, status=status.HTTP_404_NOT_FOUND)

        # Get assigned subjects and teachers for the class-section and academic year
        subjects = Subject.objects.filter(classid=class_instance)
        teachers = Employee.objects.filter(subjectteacher_set__subjectid__in=subjects).distinct()

        # Check for scheduling conflicts in the selected academic year
        conflicting_teachers = Timetable.objects.filter(academic_year=academic_year, day=day, time_slot=time_slot).values_list('teacher_id', flat=True)
        
        # Prepare subject-teacher dropdown data
        subjects_data = SubjectSerializer(subjects, many=True).data
        teachers_data = []
        for teacher in teachers:
            teachers_data.append({
                'teacher': EmployeeDetailSerializer(teacher).data,
                'disabled': teacher.empid in conflicting_teachers  # Disable if there's a conflict
            })

        return Response({
            "subjects": subjects_data,
            "teachers": teachers_data,
        }, status=status.HTTP_200_OK)

    def post(self, request):
    # Extract timetable data from request
        timetable_data = request.data.get('timetable')
        class_id = timetable_data.get('classid')
        academic_year_id = timetable_data.get('academic_year')
        subject_id = timetable_data.get('subjectid')
        teacher_id = timetable_data.get('teacherid')
        day = timetable_data.get('day')
        time_slot = timetable_data.get('time_slot')

        # Validate class, academic year, subject, and teacher
        try:
            class_instance = Class.objects.get(classid=class_id)
            academic_year = AcademicYear.objects.get(id=academic_year_id)
            subject = Subject.objects.get(subjectid=subject_id)
            teacher = Employee.objects.get(empid=teacher_id)
            
        except (Class.DoesNotExist, AcademicYear.DoesNotExist, Subject.DoesNotExist, Employee.DoesNotExist):
            return Response({"error": "Invalid class, academic year, subject, or teacher"}, status=status.HTTP_404_NOT_FOUND)

        # Check for teacher's availability at the given time slot to prevent double-booking
        if Timetable.objects.filter(
            academic_year=academic_year, teacher=teacher, day=day, time_slot=time_slot
        ).exists():
            return Response({"error": "Teacher is already assigned to another class at this time slot."}, status=status.HTTP_400_BAD_REQUEST)

        # Check for class-section time conflicts (only one subject per class-section per time slot)
        if Timetable.objects.filter(
            academic_year=academic_year, class_section=class_instance, day=day, time_slot=time_slot
        ).exists():
            return Response({"error": "This class-section already has a subject assigned at this time slot."}, status=status.HTTP_400_BAD_REQUEST)

        # Validate subject scheduling frequency (e.g., limit math to 2 times per week)
        subject_weekly_count = Timetable.objects.filter(
            academic_year=academic_year, class_section=class_instance, subject=subject, day=day
        ).count()
        subject_limit_per_week = 2  # Adjust according to your policy
        if subject_weekly_count >= subject_limit_per_week:
            return Response({"error": f"{subject.subjectname} cannot be scheduled more than {subject_limit_per_week} times per week."}, status=status.HTTP_400_BAD_REQUEST)

        # Create or update timetable entry
        Timetable.objects.update_or_create(
            academic_year=academic_year,
            class_section=class_instance,
            subject=subject,
            teacher=teacher,
            day=day,
            time_slot=time_slot
        )

        return Response({"message": "Timetable entry saved successfully."}, status=status.HTTP_200_OK)
