from django.db import models

# Create your models here.


from user.models import User


class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE,related_name="teacher_profile",null=True,blank=True)
    empid = models.CharField(max_length=20, primary_key=True, db_index=True)
    fname = models.CharField(max_length=60)
    lname = models.CharField(max_length=60)
    gender = models.CharField(max_length=10)
    dob = models.DateField(null=True)
    address = models.TextField()
    phone_number = models.CharField(max_length=20, null=True)
    email= models.EmailField()
    createdat = models.DateTimeField(auto_now_add=True)
    updatedat = models.DateTimeField(auto_now=True)
    date_of_joining = models.DateField(null=True, blank=True)
    from students.models import School
    schoolid = models.ForeignKey(School, on_delete=models.CASCADE,related_name='employee_school',null=True,blank=True)
    # status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')


    def __str__(self):
        return f"{self.fname} {self.lname}"

# class Teacher(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE,related_name="teacher_profile")
#     teacherid = models.CharField(max_length=20, primary_key=True, db_index=True)
#     tfname = models.CharField(max_length=255)
#     tlname = models.CharField(max_length=255)
#     gender = models.CharField(max_length=10)
#     dob = models.DateField()
#     address = models.TextField()
#     contactno = models.CharField(max_length=20)
#     email = models.EmailField()
#     createdat = models.DateTimeField(auto_now_add=True)
#     updatedat = models.DateTimeField(auto_now=True)
#     schoolempid = models.ForeignKey(Employee, on_delete=models.PROTECT)

#     def __str__(self):
#         return f"{self.tfname} {self.tlname}"

# class NonTeachingStaff(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="non_teaching_staff_profile") 
#     ntsid = models.CharField(max_length=20, primary_key=True, db_index=True)
#     nts_fname = models.CharField(max_length=255)
#     nts_lname = models.CharField(max_length=255)
#     gender = models.CharField(max_length=10)
#     dob = models.DateField()
#     address = models.TextField()
#     contactno = models.CharField(max_length=20)
#     emailid = models.EmailField()
#     createdat = models.DateTimeField(auto_now_add=True)
#     updatedat = models.DateTimeField(auto_now=True)
#     schoolempid = models.ForeignKey(Employee, on_delete=models.PROTECT)

#     def __str__(self):
#         return f"{self.nts_fname} {self.nts_lname}"                                                           