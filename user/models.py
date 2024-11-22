
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
import uuid
from phonenumber_field.modelfields import PhoneNumberField





class UserManager(BaseUserManager):
    def create_user(self, email, password=None,password2 = None,**extra_fields):
        if not email:        
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        extra_fields.setdefault('reg_id', str(uuid.uuid4()))
        user = self.model(email=email, **extra_fields)
       
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
      
        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    USER_TYPE_CHOICES = (
        ('student', 'Student'),
        ('parent', 'Parent'),
        ('teacher', 'Teacher'),
        ('non teacher','NonTeacher'),
        ('admin', 'Admin'),
    )
    
    email = models.EmailField(unique=True)
    fname   = models.CharField(max_length=50,blank=True,null=True)
    lname = models.CharField(max_length=50,blank=True,null=True)
    phone_number = PhoneNumberField(blank=True, null=True) 
    reset_code = models.CharField(max_length=6, blank=True, null=True)
    dob=models.DateField(blank=True,null=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    last_login = models.DateTimeField(null=True, blank=True)
    is_superuser=models.BooleanField(default=False)
    date_created=models.DateField(auto_now_add=True)
    date_updated = models.DateField(auto_now=True)
    user_type = models.CharField(max_length=100, choices=USER_TYPE_CHOICES)
    reg_id = models.CharField(max_length=100, unique=True) 
    # date_of_admission = models.DateField(null=True,blank=True)
    schoolid = models.ForeignKey('students.School', on_delete=models.PROTECT, blank=True, null=True, related_name="user_schoolid") 
    
    class Meta:
        db_table = "users"
        verbose_name_plural = "Users"
        
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['fname','lname']

    objects = UserManager()

    def __str__(self):
       return f'{self.email} ({self.get_user_type_display()})'
    
    def save(self, *args, **kwargs):
        if not self.reg_id:  
            self.reg_id = str(uuid.uuid4())
        super().save(*args, **kwargs)

class RegistrationLink(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    def __str__(self):
        return self.token
    


    
# class AttendanceReportCard(models.Model):
#     user_type = models.ForeignKey(User, on_delete=models.PROTECT)
#     term = models.CharField(max_length=50)
#     year = models.IntegerField()
#     total_days = models.IntegerField()
#     present_days = models.IntegerField()
#     absent_days = models.IntegerField()
#     late_days = models.IntegerField()

#     def __str__(self):
#         return f"{self.student} - {self.term} {self.year}"
    

