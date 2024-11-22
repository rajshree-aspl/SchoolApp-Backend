from django.db import models
# from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.crypto import get_random_string
from datetime import date



# Create your models here.




from user.models import User
# User = get_user_model()




                    
class School(models.Model):
    schoolid = models.CharField(max_length=20, primary_key=True)
    schoolname = models.CharField(max_length=255)
    schoolcode = models.CharField(max_length=100)
    createdat = models.DateTimeField(auto_now_add=True)
    updatedat = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.schoolid

class Class(models.Model):
    classid = models.AutoField(primary_key=True)
    classname = models.CharField(max_length=20)
    classcode=models.CharField(max_length=10,blank=True,null=True)
    schoolid= models.ForeignKey(School, on_delete=models.CASCADE,blank=True,null=True)
    createdat = models.DateTimeField(auto_now_add=True)
    updatedat = models.DateTimeField(auto_now=True)                                                                                                                                                                                                                        

    def __str__(self):
        return f"{self.classname}"


class Section(models.Model):
    clssectionid = models.CharField(primary_key=True,max_length=20)
    sectionname = models.CharField(max_length=20)
    classid = models.ForeignKey(Class, on_delete=models.CASCADE,related_name='section',null=True,blank=True)
    createdat = models.DateTimeField(auto_now_add=True)
    updatedat = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Set clssectionid as combination of classid and sectionname
        if not self.clssectionid:
            self.clssectionid = f"{self.classid.classname}{self.sectionname}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.clssectionid} - {self.sectionname}"

    # def __str__(self):
    #     return f"{self.clssectionid}"
    
    
from employees.models import Employee
class ClassTeacher(models.Model):
    classteacherid = models.AutoField(primary_key=True)
    teacher = models.ForeignKey(Employee,on_delete=models.CASCADE,related_name="classteacher_teacherid")
    section= models.ForeignKey(Section, on_delete=models.CASCADE,related_name="classteacher_classsecid")
    academicyear = models.CharField(max_length=20,null=True,blank=True)
    createdat = models.DateTimeField(auto_now_add=True)
    updatedat = models.DateTimeField(auto_now=True)
    

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE,related_name="student_profile")
    studentid = models.CharField(max_length=50, primary_key=True, unique=True) 
    fname = models.CharField(max_length=255, null=True)
    lname = models.CharField(max_length=255, null=True)  
    gender = models.CharField(max_length=10,null=True,blank=True)
    dob = models.DateField(null=True,blank=True)
    address = models.TextField(null=True,blank=True)
    email = models.EmailField(null=True,blank=True)
    createdat = models.DateTimeField(auto_now_add=True)
    updatedat = models.DateTimeField(auto_now=True,null=True, blank=True)
    date_of_admission = models.DateField(null=True, blank=True)
    schoolid = models.ForeignKey(School, on_delete=models.CASCADE, related_name="student_schoolid", null=True)
    clssectionid = models.ForeignKey(Section, on_delete=models.CASCADE, related_name="student_clssectionid", null=True)
    classid = models.ForeignKey(Class, on_delete=models.CASCADE, related_name="student_classid", null=True)  # New field for class assignment
    current_grade = models.CharField(max_length=10, null=True)
    academic_year = models.CharField(max_length=10, null=True)
    nationality = models.CharField(max_length=50, null=True,blank=True)
    religion = models.CharField(max_length=50, null=True,blank=True)
    languages_spoken = models.CharField(max_length=255, null=True)
    state = models.CharField(max_length=50, null=True)
    city = models.CharField(max_length=50, null=True)
    pin = models.CharField(max_length=10, null=True)
    country = models.CharField(max_length=50, null=True)
    phone_number = models.CharField(max_length=20, null=True)
    photo_id = models.CharField(max_length=100, blank=True, null=True)


    @property
    def cls_section_id(self):
        if self.clssectionid:
            return f"{self.clssectionid.classid.classname} - {self.clssectionid.sectionname}"
        return None
    
    def __str__(self):
        return f"{self.classid.classid}"
    

    def __str__(self):
        return f"{self.studentid} - {self.fname} {self.lname}"

    # def save(self, *args, **kwargs):
    #     # Populate fname and lname from user fullName if not set
    #     if self.user.fullName:
    #         parts = self.user.fullName.split(' ', 1)
    #         self.fname = parts[0]
    #         self.lname = parts[1] if len(parts) > 1 else ''
    #     super().save(*args, **kwargs)

        # # Generate studentid if not already set
        # if not self.studentid:
        #     admin_schoolid = self.user.schoolid 

        #     if admin_schoolid:
        #         # Ensure class section ID is properly retrieved (null check)
        #         class_section = self.cls_section_id if self.cls_section_id else "unknown"

        #         # Generate student ID with school ID, class/section, date of admission, and part of user ID
        #         self.studentid = f"{admin_schoolid.school_code}st{class_section}{self.date_of_admission.strftime('%m%Y')}{self.user.reg_id[:6]}"
        #     else:
        #         raise ValueError("Admin's school ID is not available or invalid.")
        # print(f"Saving student: {self.studentid}, {self.fname}, {self.lname}")
        # super(Student, self).save(*args, **kwargs)

        # import logging
        # logger = logging.getLogger(__name__)
        # logger.debug(f"Saving student: studentid={self.studentid}, fname={self.fname}, lname={self.lname}, schoolid={self.schoolid}")

        # super().save(*args, **kwargs)
        

   

class Adminrequest(models.Model):
    requested_user = models.ForeignKey(User, on_delete=models.PROTECT)
    student = models.ForeignKey(Student, on_delete=models.PROTECT,null=True)
    purpose = models.CharField(max_length=255)
    data = models.JSONField()  
    status = models.CharField(max_length=50, choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')])


class Task(models.Model):
    student = models.ForeignKey(Student, on_delete=models.PROTECT)
    teacher = models.ForeignKey(Employee, on_delete=models.PROTECT,null=True)
    task_description = models.TextField()
    is_mandatory = models.BooleanField(default=False)
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.task_description


class Parent(models.Model):
    # user = models.OneToOneField(User, on_delete=models.PROTECT,null=True, blank=True)
    parentid = models.AutoField(primary_key=True)
    mother_name=models.CharField(max_length=20,null=True,blank=True)
    father_name=models.CharField(max_length=20,null=True,blank=True)
    mother_dob=models.CharField(max_length=20,null=True,blank=True)
    father_dob=models.CharField(max_length=20,null=True,blank=True)
    address = models.TextField(null=True, blank=True)
    city = models.CharField(max_length=50, null=True, blank=True)
    state = models.CharField(max_length=50, null=True, blank=True)              
    zip_code = models.CharField(max_length=10, null=True, blank=True) 
    mother_contactno = models.CharField(max_length=20 ,null=True, blank=True)
    father_contactno = models.CharField(max_length=20 ,null=True, blank=True)
    email = models.EmailField(null=True,blank=True)
    father_aadhar = models.CharField(max_length=20, null=True, blank=True)  
    mother_aadhar = models.CharField(max_length=20, null=True, blank=True)  
    students = models.ManyToManyField(Student, through='StudentParent')
    createdat = models.DateTimeField(auto_now_add=True)
    updatedat = models.DateTimeField(auto_now=True)


    def __str__(self):
        return f"{self.mother_name}- {self.father_name}"
  
    
class StudentParent(models.Model):
    student_parent_id = models.AutoField(primary_key=True)
    student= models.ForeignKey(Student, on_delete=models.CASCADE)
    parent = models.ForeignKey(Parent, on_delete=models.CASCADE)
    createdat = models.DateTimeField(auto_now_add=True)
    updatedat = models.DateTimeField(auto_now=True)

  

    # def __str__(self):
    #     return f"{self.studentid} - {self.parentid}"
    


class MedicalInfo(models.Model):
    student = models.OneToOneField(Student, on_delete=models.CASCADE, related_name='medical_info')
    allergies = models.TextField(blank=True, null=True)
    blood_group = models.CharField(max_length=10)
    diet_needs = models.TextField(blank=True, null=True)
    Additional_info=models.CharField(max_length=100,blank=True,null=True)

    def __str__(self):
        return f"Medical Info for {self.student.fname} {self.student.lname}"

class EmergencyContact(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='emergency_contacts')
    name = models.CharField(max_length=255)
    relationship = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)

    def __str__(self):
        return f"Emergency Contact for {self.student.fname} {self.student.lname}"
    




               






class LeaveApplication(models.Model):
    STATUS_CHOICES = [
        ('NotSeen', 'Not Seen'),
        ('Seen', 'Seen'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]
 
    
    
    # leave_id = models.AutoField(primary_key=True)
    LEAVE_TYPE=[
        
        ('SL', 'sick leave'),
        ('CL', 'casual leave'),
        ('STL', 'study leave'),

    ]
    leave_id = models.AutoField(primary_key=True)
    start_date = models.DateField()
    end_date = models.DateField()
    message = models.TextField(null=True,blank=True)
    status = models.CharField(max_length=30 ,choices=STATUS_CHOICES)  ## NotSeen
    user= models.ForeignKey(User, on_delete=models.PROTECT, related_name="leave_appli_user")
    applied_date = models.DateTimeField(default=timezone.now)
    total_days = models.FloatField(blank=True, null=True)
    leave_type = models.CharField(max_length=30, choices=LEAVE_TYPE)
    approver = models.ForeignKey(User, on_delete=models.PROTECT, related_name="leave_approver",null=True)
    class Meta:
        db_table = "Leave_Application"
        verbose_name_plural = "Leave Applications"

    def __str__(self) -> str:
        return f"{self.leave_id}"


    def clean(self):
     
        super().clean()

        if self.start_date > self.end_date:
            raise ValidationError(_("The start date cannot be later than the end date."))
        num_total_date = (self.end_date - self.start_date).days
        if num_total_date < 1:
            if self.end_date == self.start_date:
                if self.end_half == self.start_half:
                    num_total_date = 0.5
                else:
                    num_total_date = 1
        self.total_days = num_total_date



class Holiday(models.Model):
    holiday_id = models.AutoField(primary_key=True)
    date = models.DateField()
    description = models.TextField()




class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  
    leave_application = models.ForeignKey(LeaveApplication, on_delete=models.CASCADE,related_name='notification_leaveapp') 
    message = models.TextField()  
    action = models.CharField(max_length=50, choices=[('Approved', 'Approved'), ('Rejected', 'Rejected')], null=True, blank=True)  

    def __str__(self):
        return f"Notification for {self.user.username}: {self.message}"

class Attendance(models.Model):
    STATUS_CHOICES = [
        ('Present', 'Present'),
        ('Absent', 'Absent'),
        ('Late to school', 'Late to school'),
    ]
    user= models.ForeignKey(User, on_delete=models.CASCADE,null=True,blank=True)
    date = models.DateField()
    status = models.CharField(max_length=20,choices=STATUS_CHOICES,default='Present')
    remarks = models.TextField(null=True, blank=True)
    session_type = models.CharField(max_length=10, choices=[('morning', 'Morning'), ('afternoon', 'Afternoon')],null=True,blank=True)
    class_schedule = models.ForeignKey('academics.ClassSchedule', on_delete=models.CASCADE,null=True,blank=True)
    
    class Meta:
        unique_together = ('user', 'date')
    

    


class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField(default=timezone.now)
    user= models.ForeignKey(User, on_delete=models.PROTECT)

    def __str__(self):
        return self.title
    



    

