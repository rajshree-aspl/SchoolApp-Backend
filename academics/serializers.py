from .models import ClassSchedule,Syllabus
from rest_framework import serializers
from .models import Period,SubjectTeacher
from user.models import User


class ClassScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassSchedule
        fields = '__all__'

class SyllabusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Syllabus
        fields = '__all__'


class PeriodSerializer(serializers.ModelSerializer):
    subject = serializers.CharField(source='subject_teacher_id.subjectid.subjectname')
    section = serializers.CharField(source='clssectionid.name')

    class Meta:
        model = Period
        fields = ['day', 'timestart', 'timeend', 'subject', 'section']

class SubjectTeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubjectTeacher
        fields = ['subjectid', 'teacherid', 'createdat', 'updatedat']




# serializers.py


# class SubjectSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Subject
#         fields = '__all__'

# class ClassSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Class
#         fields = '__all__'


from rest_framework import serializers
from students.models import Class, Section, ClassTeacher,Attendance
from employees.models import Employee
from rest_framework import serializers
from students.models import Class, Section, ClassTeacher
from .models import Subject


class SubjectSerializer(serializers.ModelSerializer):
    classcode = serializers.CharField(source='classid.classcode', read_only=True)  

    class Meta:
        model = Subject
        fields = ['subjectid', 'subjectname', 'subject_code', 'classid', 'classcode', 'category','Book_preference']
        
class SectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Section
        fields = ['sectionname', 'classid']

class ClassTeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassTeacher
        fields = ['teacher', 'academicyear', 'classsec']

class ClassSerializer(serializers.ModelSerializer):
    sections = SectionSerializer(many=True, read_only=True)
    class_teachers = ClassTeacherSerializer(many=True, read_only=True)

    class Meta:
        model = Class
        fields = ['classid', 'classname', 'classcode',  'sections', 'class_teachers']

    def create(self, validated_data):
        sections_data = validated_data.pop('sections', [])
        class_instance = Class.objects.create(**validated_data)

        for section_data in sections_data:
            section = Section.objects.create(classid=class_instance, **section_data)
            class_teacher_data = section_data.get('class_teacher')
            if class_teacher_data:
                ClassTeacher.objects.create(
                    teacher=class_teacher_data['teacher'],
                    section=section,
                    academicyear=class_teacher_data.get('academicyear', '2024-2025')
                )

        return class_instance


    









# class AttendanceSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Attendance
#         fields = ['class_schedule', 'status', 'remarks','date']


#     def save(self, **kwargs):
#         # Automatically set the user to the currently authenticated user
#         self.validated_data['user'] = self.context['request'].user
#         return super().save(**kwargs)

#     def validate_status(self, value):
#         if value not in ['Present', 'Absent', 'Late']:
#             raise serializers.ValidationError("Invalid status value. Accepted values are: Present, Absent, Late.")
#         return value
    
from django.utils import timezone

class AttendanceSerializer(serializers.ModelSerializer):
    studentid = serializers.CharField(source='user.student.studentid', read_only=True)
    
    class Meta:
        model = Attendance
        fields = ['studentid','user', 'status', 'date', 'remarks', 'session_type']  # Include session_type in fields

    def validate(self, data):
        user = data.get('user', self.instance.user if self.instance else None)
        date = data.get('date', timezone.now().date())  # Use current date if not provided
        session_type = data.get('session_type', None)  # Ensure session_type is retrieved

        # Check that session_type is provided
        if session_type not in ['morning', 'afternoon']:
            raise serializers.ValidationError("Invalid session type. It must be 'morning' or 'afternoon'.")

        # Validate that an attendance record for the same date and session type does not already exist for the user
        if not self.instance and Attendance.objects.filter(user=user, date=date, session_type=session_type).exists():
            raise serializers.ValidationError("Attendance record already exists for this user on the same date and session.")

        return data






 

