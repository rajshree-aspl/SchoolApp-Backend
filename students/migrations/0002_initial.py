# Generated by Django 5.0.2 on 2024-09-19 07:03

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('employees', '0003_initial'),
        ('students', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='adminrequest',
            name='requested_user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='attendance',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='classteacher',
            name='teacher',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='classteacher_teacherid', to='employees.teacher'),
        ),
        migrations.AddField(
            model_name='event',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='leaveapplication',
            name='approver',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='leave_approver', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='leaveapplication',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='leave_appli_user', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='notification',
            name='leave_application',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notification_leaveapp', to='students.leaveapplication'),
        ),
        migrations.AddField(
            model_name='notification',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='class',
            name='schoolid',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='students.school'),
        ),
        migrations.AddField(
            model_name='section',
            name='classid',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='students.class'),
        ),
        migrations.AddField(
            model_name='classteacher',
            name='classsec',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='classteacher_classsecid', to='students.section'),
        ),
        migrations.AddField(
            model_name='attendance',
            name='class_section',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='students.section'),
        ),
        migrations.AddField(
            model_name='student',
            name='clssectionid',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='student_clssectionid', to='students.section'),
        ),
        migrations.AddField(
            model_name='student',
            name='schoolid',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='student_schoolid', to='students.school'),
        ),
        migrations.AddField(
            model_name='student',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name='student_profile', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='medicalinfo',
            name='student',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='medical_info', to='students.student'),
        ),
        migrations.AddField(
            model_name='emergencycontact',
            name='student',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='emergency_contacts', to='students.student'),
        ),
        migrations.AddField(
            model_name='adminrequest',
            name='student',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='students.student'),
        ),
        migrations.AddField(
            model_name='studentparent',
            name='parent',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='students.parent'),
        ),
        migrations.AddField(
            model_name='studentparent',
            name='student',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='students.student'),
        ),
        migrations.AddField(
            model_name='parent',
            name='students',
            field=models.ManyToManyField(through='students.StudentParent', to='students.student'),
        ),
        migrations.AddField(
            model_name='task',
            name='student',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='students.student'),
        ),
        migrations.AddField(
            model_name='task',
            name='teacher',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='employees.teacher'),
        ),
    ]
