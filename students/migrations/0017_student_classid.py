# Generated by Django 5.0.2 on 2024-11-05 05:30

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0016_attendance_session_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='classid',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='student_classid', to='students.class'),
        ),
    ]