from django.db import models

# Create your models here.

from students.models import Student,Class,Section
from django.utils import timezone




class Subject(models.Model):
    subjectid = models.AutoField(primary_key=True)
    subjectname = models.CharField(max_length=255)
    subject_code = models.CharField(max_length=50, unique=True,null=True,blank=True)
    classid=models.ForeignKey(Class,on_delete=models.CASCADE,null=True,blank=True,related_name='subjects')
    category = models.CharField(max_length=255)
    Book_preference=models.CharField(max_length=255,null=True,blank=True)
    createdat = models.DateTimeField(auto_now_add=True)
    updatedat = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.subjectname
    
    @property
    def classcode(self):
        return self.classid.classcode 
       
from employees.models import Employee 

class SubjectTeacher(models.Model):
    subject_teacher_id = models.AutoField(primary_key=True)
    subjectid = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='subject_teachers')
    teacherid = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='subjectteacher_set')
    clssectionid = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='subjectteacher_set',null=True,blank=True)  # Added this line
    createdat = models.DateTimeField(auto_now_add=True)
    updatedat = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('subjectid','clssectionid')
 
    
class Period(models.Model):
    periodid = models.AutoField(primary_key=True)
    subject_teacher_id = models.ForeignKey(SubjectTeacher, on_delete=models.CASCADE)
    teacherid = models.ForeignKey(Employee, on_delete=models.CASCADE)
    from students.models import Student,School, Section
    clssectionid = models.ForeignKey(Section, on_delete=models.PROTECT)
    day = models.CharField(max_length=20)
    timestart = models.TimeField()
    timeend = models.TimeField()
    createdat = models.DateTimeField(auto_now_add=True)
    updatedat = models.DateTimeField(auto_now=True)
    
    
    

class Exam(models.Model):
    examid = models.AutoField(primary_key=True)
    examname = models.CharField(max_length=255)
    from students.models import Student,School, Section
    schoolid = models.ForeignKey(School, on_delete=models.PROTECT)
    clssectionid = models.ForeignKey(Section, on_delete=models.PROTECT)
    datestart = models.DateField()
    dateend = models.DateField()
    createdat = models.DateTimeField(auto_now_add=True)
    updatedat = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.examname

class Marks(models.Model):
    marksid = models.AutoField(primary_key=True)
    subjectid = models.ForeignKey(Subject, on_delete=models.PROTECT)
    examid = models.ForeignKey(Exam, on_delete=models.PROTECT)
    from students.models import Student,School, Section
    studentid = models.ForeignKey(Student, on_delete=models.PROTECT)
    clssectionid = models.ForeignKey(Section, on_delete=models.PROTECT)
    teacherid = models.ForeignKey(Employee, on_delete=models.PROTECT)
    totalmarks = models.IntegerField()
    marksobtained = models.IntegerField()
    gradeobtained = models.CharField(max_length=5)
    createdat = models.DateTimeField(auto_now_add=True)
    updatedat = models.DateTimeField(auto_now=True)

class Result(models.Model):
    resultid = models.AutoField(primary_key=True)
    examid = models.ForeignKey(Exam, on_delete=models.PROTECT)
    from students.models import Student,School, Section
    studentid = models.ForeignKey(Student, on_delete=models.PROTECT)
    marks_id = models.ForeignKey(Marks, on_delete=models.PROTECT)
    createdat = models.DateTimeField(auto_now_add=True)
    updatedat = models.DateTimeField(auto_now=True)



class ClassSchedule(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    teacher=models.ForeignKey(Employee,on_delete=models.PROTECT,default=True)
    period = models.ForeignKey(Period, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    section = models.ForeignKey(Section, on_delete=models.CASCADE,null=True,blank=True)
    date = models.DateField(default=timezone.now)
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return f'{self.subject.subjectname} - {self.start_time} to {self.end_time} for {self.student.user}'


class Syllabus(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    syllabus_text = models.TextField()
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Syllabus for {self.subject.subjectname}'
    

class AcademicYear(models.Model):
    year = models.CharField(max_length=9) 
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return self.year  
    

class Timetable(models.Model):
    class_section = models.ForeignKey(Class, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Employee, on_delete=models.CASCADE)
    day = models.CharField(max_length=10)  
    time_slot = models.TimeField() 
    academic_year=models.ForeignKey(AcademicYear,on_delete=models.CASCADE,null=True,blank=True) 

    class Meta:
        unique_together = ['class_section', 'day', 'time_slot']
