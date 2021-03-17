# Generated by Django 2.2.16 on 2021-03-12 04:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cors', '0002_corsstation_indexfile'),
    ]

    operations = [
        migrations.AddField(
            model_name='indexfile',
            name='location',
            field=models.CharField(default='http://bucket/cors/', help_text='Location Path in S3 bucket', max_length=512),
        ),
        migrations.AlterField(
            model_name='indexfile',
            name='date',
            field=models.DateTimeField(),
        ),
        migrations.AlterUniqueTogether(
            name='indexfile',
            unique_together={('file_name', 'location')},
        ),
        migrations.RemoveField(
            model_name='indexfile',
            name='file_size',
        ),
        migrations.RemoveField(
            model_name='indexfile',
            name='ftp_file_path',
        ),
        migrations.RemoveField(
            model_name='indexfile',
            name='ftp_zip_path',
        ),
        migrations.RemoveField(
            model_name='indexfile',
            name='local_path',
        ),
    ]