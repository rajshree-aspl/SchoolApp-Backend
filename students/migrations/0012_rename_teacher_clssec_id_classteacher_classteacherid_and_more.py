# Generated by Django 5.0.2 on 2024-10-08 07:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0011_alter_attendance_unique_together'),
    ]

    operations = [
        migrations.RenameField(
            model_name='classteacher',
            old_name='teacher_clssec_id',
            new_name='classteacherid',
        ),
        migrations.RenameField(
            model_name='classteacher',
            old_name='classsec',
            new_name='section',
        ),
    ]
