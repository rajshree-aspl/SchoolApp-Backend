# Generated by Django 5.0.2 on 2024-10-10 10:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0014_alter_class_schoolid_alter_section_classid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='classteacher',
            name='academicyear',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]
