# Generated by Django 2.2.15 on 2020-09-24 05:37

import cors.middleware.ftp_connection
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('cors', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CORSStation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=512, unique=True)),
                ('x', models.FloatField()),
                ('y', models.FloatField()),
                ('z', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='IndexFile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file_name', models.CharField(max_length=512)),
                ('ftp_file_path', models.CharField(help_text='The actual path of the actual file. Can be in zip.', max_length=512)),
                ('ftp_zip_path', models.CharField(blank=True, help_text='The actual zip path if filename is in a zip file.', max_length=512, null=True)),
                ('local_path', models.CharField(blank=True, help_text='The actual path of the file in local after downloaded in local.', max_length=512, null=True)),
                ('file_size', models.BigIntegerField(help_text='Size in byte')),
                ('date', models.DateField()),
                ('station', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cors.CORSStation')),
            ],
            options={
                'unique_together': {('file_name', 'ftp_file_path', 'ftp_zip_path')},
            },
            bases=(cors.middleware.ftp_connection.IndexFileFTP, models.Model),
        ),
    ]
