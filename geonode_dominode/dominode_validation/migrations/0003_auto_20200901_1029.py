# Generated by Django 3.1 on 2020-09-01 10:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dominode_validation', '0002_validationreport_report'),
    ]

    operations = [
        migrations.AlterField(
            model_name='validationreport',
            name='resource',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='validation_reports', to='dominode_validation.dominoderesource'),
        ),
    ]
