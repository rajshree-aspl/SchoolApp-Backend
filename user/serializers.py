from django.forms import EmailField
from rest_framework import serializers
from students.models import School,Class
from phonenumber_field.serializerfields import PhoneNumberField

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer,TokenBlacklistSerializer
from rest_framework_simplejwt.tokens import RefreshToken 
import jwt
# from decouple import config
from django.utils import timezone
from employees.models import Employee
from user.utils import reset_pass_otp_email
from .models import User
from students.models import Student,Parent,Section
from .validator import no_special_charecters
from django.contrib.auth import authenticate
from .models import RegistrationLink

from django.contrib.auth import get_user_model
from students.models import School
from myschoolapp import settings
from datetime import date, timedelta
from django.core.exceptions import PermissionDenied
# from .models import AttendanceReportCard


User = get_user_model()





class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
        ## send the user data to get the token
    def get_token(cls, user):
            ## check the user is verify or not
        if user is not None :
                ## generate token for the user.. it will give you refresh and access token
            token = super().get_token(user)
          
            token['email'] = user.email
           
            return token
        else:
            raise serializers.ValidationError('You are not verified')
        
        
        
class CustomTokenRefreshSerializer(TokenRefreshSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        refresh_token = RefreshToken(attrs['refresh'])
        email = refresh_token.payload.get('email')
        try:
            user = User.objects.get(email=email)
            decoded_jwt = jwt.decode(str(data['access']), settings.SECRET_KEY, algorithms=["HS256"])
            decoded_jwt['name'] = f"{user.fname} {user.lname}".strip()  
            decoded_jwt['email'] = str(user.email)
            encoded_jwt = jwt.encode(decoded_jwt, settings.SECRET_KEY, algorithm="HS256")
            data['access'] = encoded_jwt
            data['role'] = user.user_type
            user.last_login = timezone.now()
            user.save()
            return data
        except User.DoesNotExist:
            return data

        
        
class AdminUserRegistrationSerializer(serializers.ModelSerializer):
    schoolid = serializers.PrimaryKeyRelatedField(queryset=School.objects.all(), required=False)
    date_of_admission = serializers.DateField(required=False, allow_null=True)
    date_of_joining=serializers.DateField(required=False,allow_null=True)
    classid= serializers.IntegerField(required=False,allow_null=True) 
    user_type = serializers.ChoiceField(choices=[('student', 'Student'), ('teacher', 'Teacher')]) # Fix here
    # class_sec = serializers.CharField(required=False, allow_blank=True)
    


    class Meta:
        model = User
        fields = ['email', 'fname','lname','user_type', 'dob', 'phone_number', 'schoolid','date_of_admission','date_of_joining', 'classid']


    def validate_classid(self, value):
        """Custom validation for classid"""
        try:
            # Validate if class exists
            class_instance = Class.objects.get(classid=value)
            return value
        except Class.DoesNotExist:
            raise serializers.ValidationError("Class with this ID does not exist")
        
    def validate(self, attrs):
        # Ensure classid is required for students
        if attrs.get('user_type') == 'student' and not attrs.get('classid'):
            raise serializers.ValidationError({"classid": "This field is required for students."})
        return attrs

    # def validate_class_sec(self, value):
    #     """
    #     Custom validation for class_sec to handle '2A' format.
    #     Extract the class part and section part and return the corresponding Section object.
    #     """
    #     try:
    #         # Split '2A' into '2' and 'A'
    #         class_part = value[:-1]  # Extract class number, e.g., '2'
    #         section_part = value[-1]  # Extract section letter, e.g., 'A'

    #         # Fetch the corresponding Class instance
    #         class_instance = Class.objects.get(classname=class_part)

    #         # Fetch the corresponding Section instance
    #         section_instance = Section.objects.get(classid=class_instance, sectionname=section_part)

    #         return section_instance  # Return the Section object
    #     except (Class.DoesNotExist, Section.DoesNotExist):
    #         raise serializers.ValidationError(f"Invalid class or section combination: '{value}'.")
    
    def validate(self, data):
        email = data.get("email")
        dob = data.get("dob")
        user_type = data.get("user_type")
        

        if not email:
            raise serializers.ValidationError('Email is required.')

        if dob:
            today = date.today()
            if dob > today:
                raise serializers.ValidationError({'dob': 'Date of birth cannot be in the future.'})
        
        if user_type == 'admin' and not data.get('schoolid'):
            raise serializers.ValidationError({'schoolid': 'School ID is required for admin users.'})
        # if user_type == 'student':
        #     if not date_of_admission:
        #         raise serializers.ValidationError({'date_of_admission': 'Date of admission is required for students.'})
        #     if not class_sec:
        #         raise serializers.ValidationError({'class_sec': 'Class section is required for students.'})
        return data
    
    # def validate_class_sec(self, value):
    #     """
    #     Custom validation for class_sec to handle '2A' format.
    #     Extract the class part and section part and return the corresponding Section object.
    #     """
    #     try:
    #         class_part = value[:-1]  # Extract class number, e.g., '2'
    #         section_part = value[-1]  # Extract section letter, e.g., 'A'

    #         # Fetch the Class instance
    #         class_instance = Class.objects.get(classname=class_part)

    #         # Fetch the Section instance
    #         section_instance = Section.objects.get(classid=class_instance, sectionname=section_part)

    #         return section_instance  # Return the Section object
    #     except (Class.DoesNotExist, Section.DoesNotExist):
    #         raise serializers.ValidationError(f"Invalid class or section combination: '{value}'.")


    # def create(self, validated_data):
    #     user = User.objects.create(**validated_data)
    #     return user
    
    


class UserSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(write_only=True)
    reset_code = serializers.CharField(write_only=True, required=False, allow_blank=True)
    schoolid = serializers.PrimaryKeyRelatedField(queryset=School.objects.all(), required=False, allow_null=True)

    class Meta:
        model = User
        fields = [
            'id', 'email', 'fname','lname','phone_number','dob',
            'user_type', 'reg_id',  'date_created', 'date_updated', 'schoolid',
            'password', 'password2', 'reset_code'
        ]
        extra_kwargs = {
            'password': {'write_only': True},
            'password2': {'write_only': True},
            'reset_code': {'write_only': True, 'required': False, 'allow_blank': True},
        }

    def validate(self, data):
        if "email" not in data or data["email"] is None:
            raise serializers.ValidationError('Email is required.')
        if "password" in data and len(data["password"]) < 8:
            raise serializers.ValidationError('Password must be at least 8 characters long.')
        if data.get("password") != data.get("password2"):
            raise serializers.ValidationError('Password and Confirm Password do not match.')
        return data

    def create(self, validated_data):
        reset_code = validated_data.pop('reset_code', None)
        user = User.objects.create_user(**validated_data)
        return user


class CompleteRegistrationSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(write_only=True, required=True)


    class Meta:
        model = User
        fields = ['password', 'password2']
        extra_kwargs = {
            'password': {'write_only': True},
             
        }

    def validate(self, data):
        if "password" in data and len(data["password"]) < 8:
            raise serializers.ValidationError('Password must be at least 8 characters long.')
        if data['password'] != data['password2']:
            raise serializers.ValidationError("Passwords do not match.")
        return data

    def save(self, **kwargs):
        user = self.instance
    
        print(f"Saving user: {user.email}")
       

        user.set_password(self.validated_data['password'])
        user.is_active = True
        user.save()
        return user
    



class UserProfileSerializer(serializers.ModelSerializer):
    # Custom format for created_at and last_login fields
    created_at = serializers.DateField(format="%d/%m/%Y", source="date_created", read_only=True)
    last_login = serializers.DateTimeField(format="%d/%m/%Y %H:%M:%S", read_only=True)
    schoolid = serializers.PrimaryKeyRelatedField(queryset=School.objects.all(), required=False, allow_null=True)

    class Meta:
        model = User
        fields = [
            'id','email', 'fname', 'lname', 'created_at', 'last_login', 'is_admin', 'is_staff', 'is_active',
            'phone_number', 'dob', 'reg_id', 'schoolid', 'user_type'
        ]

    def to_representation(self, instance):
        # Get the base representation of the data
        data = super().to_representation(instance)
        # Get the current user from the context
        user = self.context.get("user")

        # Conditionally exclude the last_login field if the user is not a manager
        if not getattr(user, "is_admin", False):
            data.pop("last_login", None)

        return data

    

class ParentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parent
        fields = ['user', 'parentid', 'parentname', 'gender', 'address', 'contactno', 'email', 'createdat', 'updatedat', 'studentid']
# class TeacherSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Teacher
#         fields = ['user', 'teacherid', 'tfname', 'tlname', 'gender', 'dob', 'address', 'contactno', 'email', 'createdat', 'updatedat']
        


class RegistrationLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = RegistrationLink
        fields = '__all__'

class EmployeeSerializer(serializers.ModelSerializer):


    class Meta:
        model = Employee
        fields = '__all__'


class StudentProfileSerializer(serializers.ModelSerializer):
    

    class Meta:
        model = Student
        fields = [
            'studentid', 'fname', 'lname', 'gender', 'dob', 'address',
            'contactno', 'email', 'date_of_admission', 'schoolid', 'clssectionid',
            'current_grade', 'academic_year', 'nationality', 'religion',
            'languages_spoken', 'state', 'city', 'pin', 'country', 'phone_number',
            'photo_id', 'createdat', 'updatedat'
        ]
       


                ## This is for login page




class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
                   
        if email and password:
            # #Authenticate user with email and password
            user = authenticate(email=email, password=password)

            if user:
                data['user'] = user
            else:
                raise serializers.ValidationError('Unable to log in with provided credentials.')
        else:
            raise serializers.ValidationError('Must include both email and password.')

        return data
    







class StudentCreationSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Student
        fields = ['user', 'schoolid', 'clssectionid']  # Replaced 'student_class' with 'clssectionid'

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = User.objects.create(**user_data)
        student = Student.objects.create(user=user, **validated_data)
        return student

        
        

           

class CustomTokenBlacklistSerializer(TokenBlacklistSerializer):
    def validate(self, attrs):
        refresh = attrs.get("refresh")
        token = RefreshToken(refresh).blacklist()
        return "success"

