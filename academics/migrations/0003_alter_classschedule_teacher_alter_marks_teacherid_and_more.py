# Generated by Django 5.0.2 on 2024-09-23 09:22

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('academics', '0002_initial'),
        ('employees', '0003_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='classschedule',
            name='teacher',
            field=models.ForeignKey(default=True, on_delete=django.db.models.deletion.PROTECT, to='employees.employee'),
        ),
        migrations.AlterField(
            model_name='marks',
            name='teacherid',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='employees.employee'),
        ),
        migrations.AlterField(
            model_name='period',
            name='teacherid',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='employees.employee'),
        ),
        migrations.AlterField(
            model_name='subjectteacher',
            name='teacherid',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='employees.employee'),
        ),
    ]
