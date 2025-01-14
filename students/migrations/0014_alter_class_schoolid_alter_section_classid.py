# Generated by Django 5.0.2 on 2024-10-08 11:52

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0013_class_classcode_alter_class_classname'),
    ]

    operations = [
        migrations.AlterField(
            model_name='class',
            name='schoolid',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='students.school'),
        ),
        migrations.AlterField(
            model_name='section',
            name='classid',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='section', to='students.class'),
        ),
    ]
