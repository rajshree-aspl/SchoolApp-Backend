# Generated by Django 5.0.2 on 2024-09-24 11:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0007_alter_section_classid'),
    ]

    operations = [
        migrations.AddField(
            model_name='medicalinfo',
            name='Additional_info',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
