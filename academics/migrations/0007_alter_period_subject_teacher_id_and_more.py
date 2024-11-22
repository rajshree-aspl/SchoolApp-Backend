# Generated by Django 5.0.2 on 2024-10-17 07:47

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('academics', '0006_subject_book_preference'),
        ('employees', '0009_remove_employee_employee_role'),
    ]

    operations = [
        migrations.AlterField(
            model_name='period',
            name='subject_teacher_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='academics.subjectteacher'),
        ),
        migrations.AlterField(
            model_name='period',
            name='teacherid',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='employees.employee'),
        ),
        migrations.AlterUniqueTogether(
            name='subjectteacher',
            unique_together={('subjectid', 'teacherid')},
        ),
    ]
