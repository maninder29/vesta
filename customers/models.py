from .choices import *
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.conf import settings
from feedback.models import *
import os
import time

class Tag(models.Model):
	name=models.CharField(max_length=50)
	def __unicode__(self):
		return self.name

class Subtag(models.Model):
	tag=models.ForeignKey(Tag)
	name=models.CharField(max_length=50)
	def __unicode__(self):
		return self.name

class Address(models.Model):
	address=models.TextField(default='NA')
	latitude=models.CharField(max_length=30, default='28.6')
	longitude=models.CharField(max_length=30, default='77.2')
	def __unicode__(self):
		return self.address

class Phone(models.Model):
	phone=models.CharField(max_length=13, default='NA')
	def __unicode__(self):
		return self.phone

def dp_upload(instance, filename):
	timestr = time.strftime("%Y%m%d-%H%M%S")
	ext = filename[::-1].split('.')[0][::-1]
	filename = timestr + '.' + ext
	x = instance.user
	if x.email:
		return '{0}/dp/{1}'.format(x.email, filename)
	else:
		return 'inactive_users_dp/{0}/{1}'.format(x.username, filename)

def thumbnail_upload(instance, filename):
	timestr = time.strftime("%Y%m%d-%H%M%S")
	ext = filename[::-1].split('.')[0][::-1]
	filename = timestr + '-thumb.' + ext
	x = instance.user
	if x.email:
		return '{0}/dp/{1}'.format(x.email, filename)
	else:
		return 'inactive_users_dp/{0}/{1}'.format(x.username, filename)

def cover_upload(instance, filename):
	timestr = time.strftime("%Y%m%d-%H%M%S")
	ext = filename[::-1].split('.')[0][::-1]
	filename = timestr + '.' + ext
	x = instance.user
	if x.email:
		return '{0}/cover/{1}'.format(x.email, filename)
	else:
		return 'inactive_users_dp/{0}/{1}'.format(x.username, filename)


class Profile(models.Model):
	user=models.OneToOneField(User)
	name=models.CharField(max_length=60, default='Vesta user')
	dp=models.ImageField(upload_to=dp_upload, null=True, blank=True)
	thumbnail=models.ImageField(upload_to=thumbnail_upload, null=True, blank=True)
	cover=models.ImageField(upload_to=cover_upload, null=True, blank=True)
	phone=models.OneToOneField(Phone, null=True, blank=True)
	age=models.CharField(max_length=3, default='0')
	gender=models.CharField(max_length=20, default='male')
	address=models.OneToOneField(Address, null=True, blank=True)
	vip=models.BooleanField(default=False)
	def __unicode__(self):
		user=self.user
		return user.email if user.email else user.username

	@property
	def dp_url(self):
		if self.dp and hasattr(self.dp, 'url'):
			return self.dp.url
		else:
			return '/static/img/default-user.jpg'

	@property
	def thumbnail_url(self):
		if self.thumbnail and hasattr(self.thumbnail, 'url'):
			return self.thumbnail.url
		else:
			return '/static/img/default-thumbnail.jpg'

	@property
	def cover_url(self):
		if self.cover and hasattr(self.cover, 'url'):
			return self.cover.url
		else:
			return '/static/img/sunset.jpg'

	@property
	def type(self):
		try:
			x=self.patient
			return "patient"
		except:
			try:
				x=self.doctor
				return "doctor"
			except:
				try:
					x=self.student
					return "student"
				except:
					try:
						x=self.fitnessenthusiast
						return "fitness_enthusiast"
					except:
						return "Unknown"

	@property
	def votes(self):
		user=self.user
		ratings=Rating.objects.filter(user=user)
		return len(ratings)

	@property
	def rating(self):
		user=self.user
		ratings=Rating.objects.filter(user=user)
		sum=0
		for rating in ratings:
			sum += rating.value
		try:
			return round(float(sum)/(self.votes), 1)
		except:
			return 0


class Setting(models.Model):
	profile=models.OneToOneField(Profile)
	PAGE_CHOICES=page_choices
	default_page=models.CharField(max_length=12, choices=PAGE_CHOICES, default='mySpace')
	def __unicode__(self):
		return str(self.profile.user.email)


class FCMDevice(models.Model):
	profile=models.ForeignKey(Profile)
	registration_id=models.TextField()
	def __unicode__(self):
		return self.profile.user.email


class Patient(models.Model):
	profile=models.OneToOneField(Profile)
	diseases=models.ManyToManyField('Disease', blank=True)
	def __unicode__(self):
		return str(self.profile)

class Doctor(models.Model):
	profile=models.OneToOneField(Profile)
	qualification=models.ManyToManyField('Degree', blank=True)
	speciality=models.ManyToManyField('Speciality', blank=True)
	experience=models.TextField(default='none')
	def __unicode__(self):
		return str(self.profile)

class Student(models.Model):
	profile=models.OneToOneField(Profile)
	qualification=models.ManyToManyField('Degree', blank=True)
	university=models.CharField(max_length=120, default='none')
	def __unicode__(self):
		return str(self.profile)

class FitnessEnthusiast(models.Model):
	profile=models.OneToOneField(Profile)
	interests=models.ManyToManyField('Interests', blank=True)
	def __unicode__(self):
		return str(self.profile)


class Interests(models.Model):
	INTEREST_CHOICES=interest_choices
	name=models.CharField(max_length=2, choices=INTEREST_CHOICES, primary_key=True)
	def __unicode__(self):
		return self.name

class Degree(models.Model):
	DEGREE_CHOICES=degree_choices
	name=models.CharField(max_length=2, choices=DEGREE_CHOICES, primary_key=True)
	def __unicode__(self):
		return self.name

class Speciality(models.Model):
	SPECIALITY_CHOICES=speciality_choices
	name=models.CharField(max_length=2, choices=SPECIALITY_CHOICES, primary_key=True)
	def __unicode__(self):
		return self.name
	class Meta:
		verbose_name_plural="Specialities"

class Disease(models.Model):
	DISEASE_CHOICES=disease_choices
	name=models.CharField(max_length=2, choices=DISEASE_CHOICES, primary_key=True)
	def __unicode__(self):
		return self.name

"""
from bs4 import BeautifulSoup
import urllib2
url = "http://www.webmd.com/health-insurance/tc/medical-specialists-medical-specialists"
content = urllib2.urlopen(url).read()
soup = BeautifulSoup(content)
for x in soup.find_all('ul')[29].find_all('li'):
	print x.find('a').text

"""


# class Lab(models.Model):
# 	profile=models.OneToOneField(Profile)
# 	def __unicode__(self):
# 		return str(self.profile.user.get_full_name())

# class Pharmacy(models.Model):
# 	profile=models.OneToOneField(Profile)
# 	def __unicode__(self):
# 		return str(self.profile.user.get_full_name())

# class Clinic(models.Model):
# 	name=models.CharField(max_length=50)
# 	dp=models.ImageField(upload_to=dp_upload, null=True, blank=True)
# 	phone=models.OneToOneField(Phone, null=True, blank=True)
# 	address=models.OneToOneField(Address, null=True, blank=True)
# 	is_active=models.BooleanField(default=True)
# 	tags=models.ManyToManyField(Tag, blank=True)
# 	class Meta:
# 		unique_together=('name', 'address')

# 	def __unicode__(self):
# 		return self.name
# 	@property
# 	def dp_url(self):
# 		if self.dp and hasattr(self.dp, 'url'):
# 			return self.dp.url
# 		else:
# 			return '/static/img/clinic-logo.jpg'

# 	@property
# 	def votes(self):
# 		return global_votes(self)

# 	@property
# 	def rating(self):
# 		return global_rating(self)


# class Test(models.Model):
# 	name=models.CharField(max_length=50)
# 	lab=models.ForeignKey(Lab)
# 	fees=models.IntegerField(default=0)
# 	def __unicode__(self):
# 		return str(self.name)


# class DoctorFee(models.Model):
# 	doctor=models.ForeignKey(Doctor)
# 	clinic=models.ForeignKey(Clinic)
# 	fees=models.IntegerField(default=0)
# 	def __unicode__(self):
# 		return str(self.doctor)+'-'+str(self.clinic)


# class ClinicSchedule(models.Model):
# 	clinic=models.ForeignKey(Clinic)
# 	doctor=models.ForeignKey(Doctor)
# 	day=models.CharField(max_length=9)
# 	start=models.TimeField()
# 	end=models.TimeField()
# 	max_token=models.IntegerField(default=50)
# 	active=models.BooleanField(default=True)
# 	def __unicode__(self):
# 		return str(self.clinic)+"/ Dr."+str(self.doctor)+"/"+str(self.day)+"/"+str(self.start)+"-"+str(self.end)


# class LabSchedule(models.Model):
# 	test=models.ForeignKey(Test)
# 	day=models.CharField(max_length=9)
# 	start=models.TimeField()
# 	end=models.TimeField()
# 	max_token=models.IntegerField(default=50)
# 	active=models.BooleanField(default=True)
# 	def __unicode__(self):
# 		return str(self.test)+" - "+str(self.day)+" - "+str(self.start)+" - "+str(self.end)


# class ClinicAppointment(models.Model):
# 	patient=models.ForeignKey(Patient)
# 	doctor=models.ForeignKey(Doctor)
# 	clinic=models.ForeignKey(Clinic)
# 	date=models.DateField()
# 	time=models.TimeField()
# 	token=models.IntegerField()
# 	active=models.BooleanField(default=True)
# 	timestamp=models.DateTimeField(auto_now=False, auto_now_add=True)
# 	query=models.TextField(default='')
# 	def __unicode__(self):
# 		return str(self.patient)+" with Dr."+str(self.doctor)+" at "+str(self.clinic)+" on "+str(self.date)	

# class OfflineClinicAppointment(models.Model):
# 	name=models.CharField(max_length=30, default='')
# 	age=models.CharField(max_length=3, default='0')
# 	gender=models.CharField(max_length=20, default='male')
# 	doctor=models.ForeignKey(Doctor)
# 	clinic=models.ForeignKey(Clinic)
# 	token=models.IntegerField()
# 	timestamp=models.DateTimeField(auto_now=False, auto_now_add=True)
# 	def __unicode__(self):
# 		return self.name+"/"+str(self.doctor)

# class LabAppointment(models.Model):
# 	patient=models.ForeignKey(Patient)
# 	test=models.ForeignKey(Test)
# 	date=models.DateField()
# 	time=models.TimeField()
# 	token=models.IntegerField()
# 	active=models.BooleanField(default=True)
# 	timestamp=models.DateTimeField(auto_now=False, auto_now_add=True)
# 	report_generated=models.BooleanField(default=False)
# 	def __unicode__(self):
# 		return str(self.patient)+" did "+str(self.test.name)+" at "+str(self.test.lab)+" on "+str(self.date)	

# class OfflineLabAppointment(models.Model):
# 	name=models.CharField(max_length=30, default='')
# 	age=models.CharField(max_length=3, default='0')
# 	gender=models.CharField(max_length=20, default='male')
# 	test=models.ForeignKey(Test)
# 	token=models.IntegerField()
# 	timestamp=models.DateTimeField(auto_now=False, auto_now_add=True)
# 	def __unicode__(self):
# 		return self.name+"/"+str(self.doctor)

# class ClinicTokenStatus(models.Model):
# 	clinic=models.ForeignKey(Clinic)
# 	doctor=models.ForeignKey(Doctor)
# 	date=models.DateField()
# 	token=models.IntegerField(default=0)
# 	def __unicode__(self):
# 		return str(self.clinic)+"-"+str(self.doctor)+"-"+str(self.date)+" # "+str(self.token)


# class LabTokenStatus(models.Model):
# 	test=models.ForeignKey(Test)
# 	date=models.DateField()
# 	token=models.IntegerField(default=0)
# 	def __unicode__(self):
# 		return str(self.test.lab)+"-"+str(self.test)+"-"+str(self.date)+" # "+str(self.token)


# def clinic_slip_upload(instance, filename):
#     return '{0}/slip/{1}'.format(instance.patient.user.email, filename)


# class ClinicSlip(models.Model):
# 	patient=models.ForeignKey(Patient)
# 	doctor=models.ForeignKey(Doctor)
# 	clinic=models.ForeignKey(Clinic)
# 	disease_name=models.CharField(max_length=50)
# 	prescription=models.ImageField(upload_to=clinic_slip_upload, null=True, blank=True)
# 	timestamp=models.DateTimeField(auto_now=False, auto_now_add=True)
# 	reply_by_doctor=models.OneToOneField('ClinicSlipReply', null=True, blank=True)

# 	class Meta:
# 		ordering=["-timestamp"]	
# 	def __unicode__(self):
# 		return str(self.patient)+self.disease_name


# def report_upload(instance, filename):
#     return 'reports/{}'.format(filename)

# class ClinicSlipReply(models.Model):
# 	result=models.FileField(upload_to=report_upload)
# 	confirmed=models.NullBooleanField()
# 	remarks=models.TextField(default='')
# 	def __unicode__(self):
# 		return str(self.result)


# class LabSlip(models.Model):
# 	patient=models.ForeignKey(Patient)
# 	test=models.ForeignKey(Test)
# 	result=models.FileField(upload_to=report_upload)
# 	timestamp=models.DateTimeField(auto_now=False, auto_now_add=True)

# 	class Meta:
# 		ordering=["-timestamp"]	
# 	def __unicode__(self):
# 		return str(self.patient)+'-'+str(self.test)

# def prescription_upload(instance, filename):
#     return '{0}/prescription/{1}'.format(instance.patient.user.email, filename)


# class PharmacyOrder(models.Model):
# 	patient=models.ForeignKey(Patient)
# 	pharmacy=models.ForeignKey(Pharmacy)
# 	prescription=models.ImageField(upload_to=prescription_upload)
# 	remarks=models.CharField(max_length=500, default='None')
# 	timestamp=models.DateTimeField(auto_now=False, auto_now_add=True)
# 	reply_by_pharmacy=models.OneToOneField('PharmacyOrderReply', null=True, blank=True)
# 	confirmed=models.BooleanField(default=False) #pharmacy will confirm this
# 	def __unicode__(self):
# 		return str(self.patient)

# 	class Meta:
# 		ordering=['-timestamp']

# class PharmacyOrderReply(models.Model):
# 	reply=models.TextField(default='')
# 	confirmed=models.BooleanField(default=False) #patient will confirm this
# 	def __unicode__(self):
# 		return self.reply

# class BloodPressure(models.Model):
# 	user=models.ForeignKey(Patient)
# 	date=models.DateField()
# 	low=models.IntegerField(default=0)
# 	high=models.IntegerField(default=0)
# 	class Meta:
# 		ordering=['-id']

# class Sugar(models.Model):
# 	user=models.ForeignKey(Patient)
# 	date=models.DateField()
# 	value1=models.IntegerField(default=0)
# 	class Meta:
# 		ordering=['-id']

# class Cholesterol(models.Model):
# 	user=models.ForeignKey(Patient)
# 	date=models.DateField()
# 	value2=models.IntegerField(default=0)
# 	class Meta:
# 		ordering=['-id']

# class Temperature(models.Model):
# 	user=models.ForeignKey(Patient)
# 	date=models.DateField()
# 	value3=models.IntegerField(default=0)
# 	class Meta:
# 		ordering=['-id']

# class BMI(models.Model):
# 	user=models.ForeignKey(Patient)
# 	date=models.DateField()
# 	value4=models.IntegerField(default=0)
# 	class Meta:
# 		ordering=['-id']


# class Gym(models.Model):
# 	pass

# class Mission(models.Model):
# 	CHOICES = (
# 		('easy', 'easy'),
# 		('moderate', 'moderate'),
# 		('difficult', 'difficult')
# 		)
# 	name = models.CharField(max_length=160)
# 	points = models.PositiveIntegerField(default=0)
# 	time = models.TimeField()
# 	difficulty = models.ChoiceField(choices=CHOICES)
# 	description = models.TextField()


# class Question(models.Model):
# 	mission = models.ForeignKey(Mission)
# 	question = models.TextField()
# 	media = models.ImageField()
# 	correct_answer = models.CharField(max_length=1)
# 	given_answer = models.CharField(max_length=1)

# class Answer(models.Model):
# 	question = models.ForeignKey(Question)
# 	media = models.ImageField()
# 	value = models.CharField(max_length=1)

# CREATE TABLE Mission (
#     ID int NOT NULL PRIMARY KEY AUTO_INCREMENT,
#     name varchar(255) NOT NULL,
#     points int NOT NULL,
#     time TIME NOT NULL,
#     difficulty MULTISET("easy", "moderate", "difficult") NOT NULL,
#     description varchar(255),
# );

# CREATE TABLE Question (
#     ID int NOT NULL PRIMARY KEY AUTO_INCREMENT,
#     question varchar(255) NOT NULL,
#     media varchar(255) NOT NULL, /*path to media*/
#     correct_answer varchar(1) NOT NULL,
#     given_answer varchar(1),
#     mission_id int FOREIGN KEY REFERENCES Mission(mission_id),
# );

# CREATE TABLE Answer (
#     ID int NOT NULL PRIMARY KEY AUTO_INCREMENT,
#     media varchar(255) NOT NULL, /*path to media*/
#     value int NOT NULL,
#     question_id int FOREIGN KEY REFERENCES Question(question_id),
# );