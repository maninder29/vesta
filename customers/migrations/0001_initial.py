# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-06-25 16:51
from __future__ import unicode_literals

import customers.models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address', models.TextField(default=b'NA')),
                ('latitude', models.CharField(default=b'28.6', max_length=30)),
                ('longitude', models.CharField(default=b'77.2', max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='Degree',
            fields=[
                ('name', models.CharField(choices=[(b'1', b'MBBS'), (b'2', b'MS'), (b'3', b'MD'), (b'4', b'DM')], max_length=2, primary_key=True, serialize=False)),
            ],
        ),
        migrations.CreateModel(
            name='Disease',
            fields=[
                ('name', models.CharField(choices=[(b'1', b'Multiple Sclerosis'), (b'2', b'Cancer'), (b'3', b'TB'), (b'4', b'Mental illness'), (b'5', b'Type 1 Diabetes')], max_length=2, primary_key=True, serialize=False)),
            ],
        ),
        migrations.CreateModel(
            name='Doctor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('experience', models.TextField(default=b'none')),
            ],
        ),
        migrations.CreateModel(
            name='FCMDevice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('registration_id', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='FitnessEnthusiast',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='Interests',
            fields=[
                ('name', models.CharField(choices=[(b'1', b'Body building'), (b'2', b'Dieting'), (b'3', b'Gym'), (b'4', b'Meditation'), (b'5', b'Nutrition'), (b'6', b'Physical exercise'), (b'7', b'Yoga'), (b'8', b'Running'), (b'9', b'Weight lifting'), (b'10', b'Physical fitness'), (b'11', b'Zumba'), (b'12', b'Swimming'), (b'13', b'Other')], max_length=2, primary_key=True, serialize=False)),
            ],
        ),
        migrations.CreateModel(
            name='Patient',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('diseases', models.ManyToManyField(blank=True, to='customers.Disease')),
            ],
        ),
        migrations.CreateModel(
            name='Phone',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone', models.CharField(default=b'NA', max_length=13)),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default=b'Vesta user', max_length=60)),
                ('dp', models.ImageField(blank=True, null=True, upload_to=customers.models.dp_upload)),
                ('thumbnail', models.ImageField(blank=True, null=True, upload_to=customers.models.thumbnail_upload)),
                ('cover', models.ImageField(blank=True, null=True, upload_to=customers.models.cover_upload)),
                ('age', models.CharField(default=b'0', max_length=3)),
                ('gender', models.CharField(default=b'male', max_length=20)),
                ('vip', models.BooleanField(default=False)),
                ('address', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='customers.Address')),
                ('phone', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='customers.Phone')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Setting',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('default_page', models.CharField(choices=[(b'mySpace', b'mySpace'), (b'differential', b'differential'), (b'insights', b'insights')], default=b'mySpace', max_length=12)),
                ('profile', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='customers.Profile')),
            ],
        ),
        migrations.CreateModel(
            name='Speciality',
            fields=[
                ('name', models.CharField(choices=[(b'1', b'Anesthesiologist'), (b'2', b'Cardiologist'), (b'3', b'Dermatologist'), (b'4', b'Endocrinologist'), (b'5', b'Gastroenterologist'), (b'6', b'Gynecologist'), (b'7', b'Neurologist'), (b'8', b'Obstetrician'), (b'9', b'Oncologist'), (b'10', b'Pathologist'), (b'11', b'Surgeon'), (b'12', b'Urologist')], max_length=2, primary_key=True, serialize=False)),
            ],
            options={
                'verbose_name_plural': 'Specialities',
            },
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('university', models.CharField(default=b'none', max_length=120)),
                ('profile', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='customers.Profile')),
                ('qualification', models.ManyToManyField(blank=True, to='customers.Degree')),
            ],
        ),
        migrations.CreateModel(
            name='Subtag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.AddField(
            model_name='subtag',
            name='tag',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='customers.Tag'),
        ),
        migrations.AddField(
            model_name='patient',
            name='profile',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='customers.Profile'),
        ),
        migrations.AddField(
            model_name='fitnessenthusiast',
            name='interests',
            field=models.ManyToManyField(blank=True, to='customers.Interests'),
        ),
        migrations.AddField(
            model_name='fitnessenthusiast',
            name='profile',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='customers.Profile'),
        ),
        migrations.AddField(
            model_name='fcmdevice',
            name='profile',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='customers.Profile'),
        ),
        migrations.AddField(
            model_name='doctor',
            name='profile',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='customers.Profile'),
        ),
        migrations.AddField(
            model_name='doctor',
            name='qualification',
            field=models.ManyToManyField(blank=True, to='customers.Degree'),
        ),
        migrations.AddField(
            model_name='doctor',
            name='speciality',
            field=models.ManyToManyField(blank=True, to='customers.Speciality'),
        ),
    ]
