# Generated by Django 5.0.2 on 2024-10-24 06:26

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('academics', '0010_alter_subjectteacher_teacherid'),
        ('employees', '0009_remove_employee_employee_role'),
        ('students', '0016_attendance_session_type'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='subjectteacher',
            unique_together=set(),
        ),
        migrations.AddField(
            model_name='subjectteacher',
            name='clssectionid',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='subjectteacher_set', to='students.section'),
        ),
        migrations.AlterUniqueTogether(
            name='subjectteacher',
            unique_together={('subjectid', 'teacherid', 'clssectionid')},
        ),
    ]