from rest_framework import serializers
from .models import Parent, Student, Adminrequest, LeaveApplication, Holiday


from rest_framework import serializers
from .models import Student, School, Section,Notification
from rest_framework import serializers
from .models import School, Section,Task,Class,ClassTeacher,Event,StudentParent
from .models import LeaveApplication
from django.utils import timezone
from students.models import Attendance,MedicalInfo,EmergencyContact


class SchoolSerializer(serializers.ModelSerializer):
    class Meta:
        model = School
        fields = '__all__'

class SectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Section
        fields = '__all__'  # Assuming these serializers exist

class StudentSerializer(serializers.ModelSerializer):
    createdat = serializers.DateTimeField(format="%Y-%m-%d")
    updatedat = serializers.DateTimeField(format="%Y-%m-%d")
    date_of_admission = serializers.DateField(format="%Y-%m-%d", required=False)


    schoolid = serializers.PrimaryKeyRelatedField(queryset=School.objects.all())
    clssectionid = serializers.PrimaryKeyRelatedField(queryset=Section.objects.all(), required=False)

    class Meta:
        model = Student
        fields = [
            'studentid', 'user', 'fname', 'lname', 'gender', 'dob', 'address', 'contactno', 'email', 
            'createdat', 'updatedat', 'schoolid', 'clssectionid', 'current_grade', 'academic_year', 
            'nationality', 'religion', 'languages_spoken', 'state', 'city', 'pin', 'country', 'phone_number',
            'photo_id'
        ]

    def create(self, validated_data):
        request = self.context.get('request')
        admin = request.user

        if not admin.is_staff:
            raise serializers.ValidationError('Only admins can create students.')

        # Ensure admin has a schoolid
        if not admin.schoolid:
            raise serializers.ValidationError('Admin must have a school ID.')

        # Use the admin's schoolid in the student creation
        validated_data['schoolid'] = admin.schoolid

        # Create the student
        student = Student.objects.create(**validated_data)
        return student



class StudentUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields="__all__"

   

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['user', 'leave_application', 'message', 'action', 'created_at']
class AdminrequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Adminrequest
        fields = '__all__'
class AdminrequestlistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Adminrequest
        exclude=["data"]


class ParentSerializer(serializers.ModelSerializer):
    class Meta:
        model =Parent
        fields='__all__'


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'task_description', 'is_mandatory', 'is_completed', 'created_at']
        extra_kwargs = {
            'task_description': {'required': True}
        }
         
    def validate_task_description(self, value):
        if not value:
            raise serializers.ValidationError("Task description cannot be null.")
        return value



class HolidaySerializer(serializers.ModelSerializer):
    class Meta:
        model = Holiday
        fields = '__all__'

    

class LeaveApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveApplication
        fields = ['start_date', 'end_date', 'message', 'leave_type']

    def validate(self, attrs):
        start_date = attrs['start_date']
        end_date = attrs['end_date']
        
        if end_date < timezone.now().date():
            raise serializers.ValidationError("You cannot apply for leave for past dates.")

        if start_date > end_date:
            raise serializers.ValidationError("Start date must be before or equal to end date.")

        return attrs

    def create(self, validated_data):
        user = self.context.get('request').user
        validated_data['user'] = user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        instance.start_date = validated_data.get('start_date', instance.start_date)
        instance.end_date = validated_data.get('end_date', instance.end_date)
        instance.message = validated_data.get('message', instance.message)
        instance.leave_type = validated_data.get('leave_type', instance.leave_type)
        instance.save()
        return instance

class LeaveApplicationRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveApplication
        fields = '__all__'

class AttendanceReportSerializer(serializers.Serializer):
    total_school_days = serializers.IntegerField()
    school_days_so_far = serializers.IntegerField()
    days_present = serializers.IntegerField()
    days_absent = serializers.IntegerField()
    vacation_days = serializers.IntegerField()
    sick_days = serializers.IntegerField()
    other_days = serializers.IntegerField()

class AttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = '__all__'





class ClassSerializer(serializers.ModelSerializer):
    schoolid = SchoolSerializer()  

    class Meta:
        model = Class
        fields = ['classid', 'classname', 'schoolid', 'createdat', 'updatedat']
        read_only_fields = ['createdat', 'updatedat']

class SectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Section
        fields = ['clssectionid', 'sectionname', 'classid', 'createdat', 'updatedat']
        read_only_fields = ['createdat', 'updatedat']

# class ClassTeacherSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = ClassTeacher
#         fields = ['teacher_clssec_id', 'teacher', 'classsec', 'academicyear', 'createdat', 'updatedat']
#         read_only_fields = ['createdat', 'updatedat']



class ParentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parent
        fields = ['parentid', "mother_name","father_name", "mother_dob","father_dob", 'address', 'city', 'state', 'zip_code', "father_contactno","mother_contactno",'email', 'father_aadhar', 'mother_aadhar']

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ['title', 'start_date', 'end_date', 'description']

class MedicalInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicalInfo
        fields = ['allergies', 'blood_group', 'diet_needs']

class EmergencyContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmergencyContact
        fields = ['name', 'relationship', 'phone_number', 'email']



class StudentSerializer(serializers.ModelSerializer):
    parents = ParentSerializer(many=True, read_only=True)
    medical_info = MedicalInfoSerializer(read_only=True)
    emergency_contacts = EmergencyContactSerializer(many=True, read_only=True)

    class Meta:
        model = Student
        fields = [
            'user','studentid', 'fname', 'lname', 'gender', 'dob', 'address','email',
            'createdat', 'updatedat', 'date_of_admission', 'schoolid', 'clssectionid',
            'current_grade', 'academic_year', 'nationality', 'religion', 'languages_spoken',
            'state', 'city', 'pin', 'country', 'phone_number', 'photo_id',
            'parents', 'medical_info', 'emergency_contacts'
        ]



class StudentParentSerializer(serializers.ModelSerializer):
    student = StudentSerializer()
    parent = ParentSerializer()

    class Meta:
        model = StudentParent
        fields = ['student', 'parent', 'createdat', 'updatedat']


from .models import MedicalInfo, EmergencyContact

class MedicalInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicalInfo
        fields = ['allergies', 'blood_group', 'diet_needs', 'Additional_info']

class EmergencyContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmergencyContact
        fields = ['name', 'relationship', 'phone_number', 'email']




# class ClassTeacherSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = ClassTeacher
#         fields = ['teacher','section', 'academicyear', 'createdat', 'updatedat']

from academics.serializers import SubjectTeacherSerializer
from employees.models import Employee
from academics.models import SubjectTeacher,Subject
# class EmployeeDetailSerializer(serializers.ModelSerializer):

#     class_teachers = ClassTeacherSerializer(many=True, read_only=True, source='classteacher_teacherid')
#     subjects = SubjectTeacherSerializer(many=True, read_only=True, source='subjectteacher_teacherid')

#     class Meta:
#         model = Employee
#         fields = '__all__'

class ClassTeacherSerializer(serializers.ModelSerializer):
    section_name = serializers.CharField(source='section.sectionname', read_only=True)

    class Meta:
        model = ClassTeacher
        fields = ['section_name', 'academicyear', 'createdat', 'updatedat']


class SubjectPreferenceSerializer(serializers.ModelSerializer):
    subject_id = serializers.PrimaryKeyRelatedField(queryset=Subject.objects.all(), source='subjectid')
    subject_name = serializers.CharField(source='subjectid.subjectname', read_only=True)
    teacher_name = serializers.CharField(source='teacherid.fname', read_only=True)  # Display subject name

    class Meta:
        model = SubjectTeacher
        fields = ['subject_teacher_id', 'subject_id', 'subject_name', 'teacherid', 'teacher_name', 'createdat', 'updatedat']



class SubjectTeacherSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source='subjectid.subjectname', read_only=True)
    teacher_name = serializers.CharField(source='teacherid.fname', read_only=True)

    class Meta:
        model = SubjectTeacher
        fields = ['subject_name','teacher_name']


class EmployeeListSerializer(serializers.ModelSerializer):
    teaching_subjects = SubjectTeacherSerializer(source='subjectteacher_set', many=True, read_only=True)
    classes_taken = ClassTeacherSerializer(source='classteacher_teacherid', many=True, read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = Employee
        fields = ['empid', 'fname', 'lname', 'teaching_subjects', 'classes_taken','email']


class EmployeeDetailSerializer(serializers.ModelSerializer):
    class_teachers = ClassTeacherSerializer(source='classteacher_teacherid', many=True, read_only=True)
    subjects_taught = SubjectTeacherSerializer(source='subjectteacher_set', many=True, read_only=True)
    subject_preferences = SubjectPreferenceSerializer(source='subjectteacher_set', many=True)
    classes_taken = ClassTeacherSerializer(source='classteacher_teacherid', many=True, read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    
    class Meta:
        model = Employee
        fields = ['empid', 'fname', 'lname', 'gender', 'dob', 'address', 'phone_number', 'email',
                  'date_of_joining', 'class_teachers', 'subjects_taught', 'subject_preferences', 'classes_taken']

    def update(self, instance, validated_data):
        # Extract the subject preferences from the data
        subjects_data = validated_data.pop('subjectteacher_set', None)
        instance = super().update(instance, validated_data)
        
        # If subject preferences are provided, update them
        if subjects_data:
            subject_ids = [subject_data['subjectid'] for subject_data in subjects_data]

            # Delete any subject preferences that are not in the new list
            SubjectTeacher.objects.filter(teacherid=instance).exclude(subjectid__in=subject_ids).delete()

            # Update or create new subject preferences without duplicates
            for subject_data in subjects_data:
                subject_id = subject_data['subjectid']
                # Check if the subject preference already exists to prevent duplicates
                if not SubjectTeacher.objects.filter(teacherid=instance, subjectid=subject_id).exists():
                    SubjectTeacher.objects.create(
                        teacherid=instance,
                        subjectid=subject_id
                    )
        
        return instance
