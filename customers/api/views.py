from .serializers import *
from customers.models import *
from django.conf import settings as django_settings
from django.contrib.auth.models import User
from django.core.files import File
from django.core.files.base import ContentFile
from django.core.urlresolvers import reverse
from PIL import Image
from pyfcm import FCMNotification
from rest_framework import viewsets, status, permissions
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from urlparse import urlparse
import requests, geocoder, pusher


pusher_client = pusher.Pusher( app_id='303592', key='cf69569914b189660423', secret='963493a9c905d786e4d1', cluster='ap2', ssl=True)

class FCMDeviceViewSet(viewsets.ModelViewSet):
	serializer_class=FCMDeviceSerializer
	queryset = FCMDevice.objects.all()
	def create(self, request):
		profile=request.user.profile
		registration_id=request.data.get('registration_id')
		if not FCMDevice.objects.filter(profile=profile, registration_id=registration_id).exists():
			FCMDevice(profile=profile, registration_id=registration_id ).save()
		return Response()


class UserRegisterViewSet(viewsets.ModelViewSet):
	serializer_class=UserSerializer
	queryset = User.objects.all()
	authentication_classes=[]
	permission_classes=[]
	def create(self, request):
		username=request.data.get('username')
		email=request.data.get('email')
		users = User.objects.all()
		usernames = [u.username for u in users]
		emails = [u.email for u in users]
		if username in usernames:
			return Response({'error_message': 'Username already exists'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
		if email in emails:
			return Response({'error_message': 'E-mail already exists'}, status=status.HTTP_409_CONFLICT)
		password=request.data.get('password')
		user=User( username=username, email=email )
		user.set_password(password)
		user.save()
		return Response()


class ProfileRegisterViewSet(viewsets.ModelViewSet):
	serializer_class=ProfileSerializer
	queryset = Profile.objects.all()
	def create(self, request):
		user=request.user
		name=request.data.get('name')
		email=request.data.get('email')
		dp_url=request.data.get('dp_url')
		type_of_user=request.data.get('type_of_user')
		if user.email != email:
			user.email = email
			user.save()
		try:
			profile=user.profile
		except:
			profile=Profile(user=user, name=name)
			profile.save()
		if dp_url:
			img_temp=ContentFile(requests.get(dp_url).content)
			profile.dp.save('name.jpeg', img_temp)
		if type_of_user == 'patient':
			Patient(profile=profile).save()
			TYPE = 'insights'
			content='Welcome! ' + name + ' to VestaSocial. Connect with other patients like yourself and give insights to others and get suggestions for your own problems.'
		elif type_of_user == 'doctor':
			Doctor(profile=profile).save()
			TYPE = 'differential'
			content='Welcome! ' + name + ' to VestaSocial. Connect with your peers and discuss medical diagnostics. Share medical updates and discuss amongst the professional community.'
		elif type_of_user == 'student':
			Student(profile=profile).save()
			TYPE = 'differential'
			content='Welcome! ' + name + ' to VestaSocial. Connect with your peers and discuss medical diagnostics. Share medical updates and discuss amongst the professional community.'
		elif type_of_user == 'fitness_enthusiast':
			FitnessEnthusiast(profile=profile).save()
			TYPE = 'mySpace'
			content='Welcome! ' + name + ' to VestaSocial. Connect with like minded people in Healthcare. Share thoughts,motivate People and get motivated by the community.'
		else:
			return Response({'error_message': 'Wrong choice'}, status=status.HTTP_403_FORBIDDEN)
		Setting(profile=profile, default_page=TYPE).save()

		pk=django_settings.ENV
		VESTA = Profile.objects.get(id=pk)
		WallPost( profile=VESTA, content=content, wall_profile=profile, welcome=True ).save()
		title = str(name) + " just joined VestaSocial"
		link = reverse('profile', kwargs={'id':user.id})
		key=profile.id
		for p in Profile.objects.all():
			Notification(profile=p, profile2=profile, title=title, link=link, tag='f', key=key).save()
		return Response()


class UserViewSet(viewsets.ModelViewSet):
	serializer_class=UserSerializer
	queryset = User.objects.all()
	def list(self, request):
		return Response(UserSerializer(request.user).data)


# SEARCH DOCTORS
# class DoctorViewSet(viewsets.ModelViewSet):
# 	serializer_class = DoctorSerializer
# 	queryset = Doctor.objects.filter()
# 	def list(self, request):
# 		query=request.query_params.get("q")
# 		if query:
# 			queryset=Doctor.objects.filter(
# 				Q(profile__user__username__icontains=query)|
# 				Q(profile__user__first_name__icontains=query)|
# 				Q(profile__user__last_name__icontains=query) |
# 				Q(qualification__icontains=query)|
# 				Q(speciality__icontains=query)|
# 				Q(profile__tags__name__icontains=query)
# 			).distinct()
# 		else:
# 			queryset=self.queryset
# 		return Response(DoctorSerializer(queryset, many=True).data)


# SEARCH LABS
# class LabViewSet(viewsets.ModelViewSet):
# 	serializer_class = LabSerializer
# 	queryset = Lab.objects.filter()
# 	def list(self, request):
# 		query=request.query_params.get("q")
# 		if query:
# 			queryset=Lab.objects.filter(
# 				Q(profile__user__username__icontains=query)|
# 				Q(profile__user__first_name__icontains=query)|
# 				Q(profile__user__last_name__icontains=query) |
# 				Q(profile__tags__name__icontains=query)|
# 				Q(test__name__icontains=query)
# 			).distinct()
# 		else:
# 			queryset=self.queryset
# 		return Response(LabSerializer(queryset, many=True).data)

# # SEARCH PHARMACIES
# class PharmacyViewSet(viewsets.ModelViewSet):
# 	serializer_class = PharmacySerializer
# 	queryset = Pharmacy.objects.filter()
# 	def list(self, request):
# 		query=request.query_params.get("q")
# 		if query:
# 			queryset=Pharmacy.objects.filter(
# 				Q(profile__user__username__icontains=query)|
# 				Q(profile__user__first_name__icontains=query)|
# 				Q(profile__user__last_name__icontains=query) |
# 				Q(profile__tags__name__icontains=query)
# 			).distinct()
# 		else:
# 			queryset=self.queryset
# 		print queryset
# 		return Response(PharmacySerializer(queryset, many=True).data)

# # VIEW TESTS IN A LAB
# class TestViewSet(viewsets.ModelViewSet):
# 	serializer_class = TestSerializer
# 	queryset = Test.objects.all()

# 	def list(self, request):
# 		id=request.query_params.get('id')
# 		lab=Lab.objects.get(id=id)
# 		tests=lab.test_set.all()
# 		return Response(TestSerializer(tests, many=True).data)

# PATIENT PROFILE
# class PatientProfileViewset(viewsets.ModelViewSet):
# 	serializer_class=PatientSerializer
# 	queryset = Patient.objects.all()
# 	def list(self, request):
# 		patient=request.user.patient
# 		clinic_slips=ClinicSlipSerializer(ClinicSlip.objects.filter(patient=patient), many=True)
# 		lab_slips=LabSlipSerializer(LabSlip.objects.filter(patient=patient), many=True)
# 		today=datetime.datetime.today()
# 		# past_clinic_appointments=ClinicAppointmentSerializer(ClinicAppointment.objects.filter(patient=patient, date__lt=today), many=True)
# 		future_clinic_appointments=ClinicAppointmentSerializer(ClinicAppointment.objects.filter(patient=patient, date__gte=today), many=True)
# 		# past_lab_appointments=LabAppointmentSerializer(LabAppointment.objects.filter(patient=patient, date__lt=today), many=True)
# 		future_lab_appointments=LabAppointmentSerializer(LabAppointment.objects.filter(patient=patient, date__gte=today), many=True)
# 		current_orders=PharmacyOrderSerializer(PharmacyOrder.objects.filter(patient=patient, confirmed=False), many=True)
# 		past_orders=PharmacyOrderSerializer(PharmacyOrder.objects.filter(patient=patient, confirmed=True), many=True)		
# 		context={
# 			'clinic_slips':clinic_slips.data,
# 			'lab_slips':lab_slips.data,
# 			# 'past_clinic_appointments':past_clinic_appointments.data,
# 			'future_clinic_appointments':future_clinic_appointments.data,
# 			# 'past_lab_appointments':past_lab_appointments.data,
# 			'future_lab_appointments':future_lab_appointments.data,
# 			'current_orders':current_orders.data,
# 			'past_orders':past_orders.data,
# 		}
# 		return Response(context)

# # UPLOAD PRESCRIPTION TO CLINIC SLIP
# class ClinicSlipViewSet(viewsets.ModelViewSet):
# 	serializer_class = ClinicSlipSerializer
# 	queryset=ClinicSlip.objects.all()

# 	def update(self, request, pk=None): # patient updates clinic slip by adding prescription
# 		if request.FILES:
# 			instance=ClinicSlip.objects.get(id=pk)
# 			instance.prescription=request.FILES.get('prescription')
# 			instance.save()
# 		return Response()

# SEARCH CLINICS
# class ClinicViewSet(viewsets.ModelViewSet):
# 	serializer_class = ClinicSerializer
# 	queryset = Clinic.objects.filter(is_active=True)
# 	def list(self, request):
# 		query=request.query_params.get("q")
# 		if query:
# 			queryset=Clinic.objects.filter(
# 				Q(is_active=True)&(
# 				Q(name__icontains=query)|
# 				Q(tags__name__icontains=query))
# 				).distinct()
# 		else:
# 			queryset=self.queryset
# 		return Response(ClinicSerializer(queryset, many=True).data)

# 	def retrieve(self, request, pk):
# 		clinic=Clinic.objects.get(id=pk)
# 		return Response(DetailedClinicSerializer(clinic).data)


# BOOK CLINIC APPOINTMENT
# class ClinicAppointmentViewSet(viewsets.ModelViewSet):
# 	serializer_class = ClinicAppointmentSerializer
# 	queryset = ClinicAppointment.objects.all()
# 	def list(self, request):
# 		d_id=request.query_params.get('d_id')
# 		c_id=request.query_params.get('c_id')
# 		doctor=Doctor.objects.get(id=d_id)
# 		clinic=Clinic.objects.get(id=c_id)
# 		today=datetime.datetime.today()
# 		date_list = pandas.date_range(today,today+datetime.timedelta(days=10), freq="D").date
# 		date_token_list={}
# 		for date in date_list:
# 			week_day=calendar.day_name[date.weekday()]
# 			try:
# 				schedules=ClinicSchedule.objects.filter(doctor=doctor,clinic=clinic,day=week_day)
# 				try:
# 					token=ClinicTokenStatus.objects.get(doctor=doctor, clinic=clinic, date=date).token
# 				except:
# 					t=ClinicTokenStatus(doctor=doctor, clinic=clinic, date=date)
# 					t.save()
# 					token=0
# 				if token<schedules.first().max_token:
# 					date_token_list[str(date)]=AdvancedClinicScheduleSerializer(schedules,many=True).data
# 			except:
# 				pass
# 		context={
# 			'date_token_list':date_token_list,
# 		}
# 		return Response(context)
# 	def create(self, request):
# 		doctor_id=request.data.get("doctor")
# 		doctor=Doctor.objects.get(id=doctor_id)
# 		clinic_id=request.data.get("clinic")
# 		clinic=Clinic.objects.get(id=clinic_id)
# 		sch_id=request.data.get('sch')
# 		sch=ClinicSchedule.objects.get(id=sch_id)
# 		date=request.data.get("date")
# 		query=request.data.get("query")
# 		date = parse(date).date()
# 		patient=request.user.patient
# 		t=ClinicTokenStatus.objects.get(doctor=doctor, clinic=clinic, date=date)
# 		t.token+=1
# 		token_no=t.token
# 		time = (datetime.datetime.combine(date,sch.start)+datetime.timedelta(minutes=3*(token_no-1))).time()
# 		today=datetime.datetime.now()
# 		current_time=today.time()
# 		if date == today.date() and datetime.datetime.combine(date,time)<datetime.datetime.combine(date,current_time):
# 			time=(datetime.datetime.combine(date,current_time)+datetime.timedelta(minutes=15)).time()
# 		appointment=ClinicAppointment(
# 			patient=patient,
# 			doctor=doctor,
# 			clinic=clinic,
# 			date=date,
# 			time=time,
# 			token=token_no,
# 			query=query
# 			).save()
# 		t.save()
# 		context={
# 			'token':token_no,
# 			'time':str(time),
# 			'end':str(sch.end)
# 		}
# 		return Response(context)


# BOOK LAB APPOINTMENT
# class LabAppointmentViewSet(viewsets.ModelViewSet):
# 	serializer_class = LabAppointmentSerializer
# 	queryset = LabAppointment.objects.all()
# 	def list(self, request):
# 		test_id=request.query_params.get("test")
# 		test=Test.objects.get(id=test_id)
# 		today=datetime.datetime.today()
# 		date_list = pandas.date_range(today,today+datetime.timedelta(days=10), freq="D").date
# 		date_token_list={}
# 		for date in date_list:
# 			week_day=calendar.day_name[date.weekday()]
# 			try:
# 				schedules=LabSchedule.objects.filter(test=test, day=week_day)
# 				try:
# 					token=LabTokenStatus.objects.get(test=test, date=date).token
# 				except:
# 					l=LabTokenStatus(test=test, date=date)
# 					l.save()
# 					token=0
# 				if token<schedules.first().max_token:
# 					date_token_list[str(date)]=AdvancedLabScheduleSerializer(schedules,many=True).data
# 			except:
# 				pass
			
# 		context={
# 			'date_token_list':date_token_list,
# 		}
# 		return Response(context)
# 	def create(self, request):
# 		test_id=request.data.get("test")
# 		test=Test.objects.get(id=test_id)
# 		sch_id=request.data.get('sch')
# 		sch=LabSchedule.objects.get(id=sch_id)
# 		date=request.data.get("date")
# 		date = parse(date).date()
# 		patient=request.user.patient
# 		t=LabTokenStatus.objects.get(test=test, date=date)
# 		t.token+=1
# 		token_no=t.token
# 		time = (datetime.datetime.combine(date,sch.start)+datetime.timedelta(minutes=10*(token_no-1))).time()
# 		today=datetime.datetime.now()
# 		current_time=today.time()
# 		if date == today.date() and datetime.datetime.combine(date,time)<datetime.datetime.combine(date,current_time):
# 			time=(datetime.datetime.combine(date,current_time)+datetime.timedelta(minutes=15)).time()
# 		appointment=LabAppointment(
# 			patient=patient,
# 			test=test,
# 			date=date,
# 			time=time,
# 			token=token_no
# 			).save()
# 		t.save()
# 		context={
# 			'token':token_no,
# 			'time':str(time),
# 		}
# 		return Response(context)

# # PLACE PHARMACY ORDER
# class PharmacyOrderViewSet(viewsets.ModelViewSet):
# 	parser_classes = [MultiPartParser]
# 	serializer_class = PharmacyOrderSerializer
# 	queryset = PharmacyOrder.objects.all()
# 	def create(self, request):
# 		patient=request.user.patient
# 		pid=request.data.get("pharmacy")
# 		pharmacy=Pharmacy.objects.get(id=pid)
# 		prescription=request.data.get('prescription')
# 		if not prescription:
# 			return Response(status=status.HTTP_403_FORBIDDEN)
# 		remarks=request.data.get('remarks')
# 		PharmacyOrder(
# 			patient=patient,
# 			pharmacy=pharmacy,
# 			prescription=prescription,
# 			remarks=remarks,
# 			).save()
# 		address=request.data.get('address')
# 		add=patient.address
# 		if not add:
# 			add=Address()
# 			add.address=address
# 			try:
# 				g=geocoder.google(address)
# 				add.latitude=g.latlng[0]
# 				add.longitude=g.latlng[1]
# 			except:
# 				pass
# 			add.save()
# 			patient.address=add
# 		elif add.address != address:
# 			add.address=address
# 			try:
# 				g=geocoder.google(address)
# 				add.latitude=g.latlng[0]
# 				add.longitude=g.latlng[1]
# 			except:
# 				pass
# 			add.save()
# 		ph=patient.phone
# 		phone=request.data.get('phone')
# 		if not ph:
# 			ph=Phone()
# 			ph.phone=phone
# 			ph.save()
# 			patient.phone=ph
# 		elif ph.phone != phone:
# 			ph.phone=phone
# 			ph.save()
# 		patient.save()
# 		return Response()
# 	def update(self, request, pk):
# 		o=PharmacyOrder.objects.get(pk=pk)
# 		r=o.reply_by_pharmacy
# 		r.confirmed=True
# 		r.save()
# 		return Response()


# class ClinicTokenStatusViewSet(viewsets.ModelViewSet):
# 	serializer_class = ClinicTokenStatusSerializer
# 	queryset = ClinicTokenStatus.objects.all()


# class BloodPressureViewSet(viewsets.ModelViewSet):
# 	serializer_class = BloodPressureSerializer
# 	queryset = BloodPressure.objects.all()

# 	def list(self,request):
# 		patient=request.user.patient
# 		month=request.query_params.get('month')
# 		year=request.query_params.get('year')
# 		values=BloodPressure.objects.filter(user=patient,date__year=year,date__month=month)
# 		return Response({'bp': BloodPressureSerializer(values, many=True).data})

# 	def create(self,request):
# 		patient=request.user.patient
# 		low=request.data.get('low')
# 		high=request.data.get('high')
# 		date=request.data.get("date")
# 		date = parse(date).date()
# 		obj=BloodPressure(user=patient,low=low,high=high,date=date)
# 		obj.save()
# 		return Response()

# 	def update(self, request, pk):
# 		obj=BloodPressure.objects.get(pk=pk)
# 		obj.low=request.data.get('low')
# 		obj.high=request.data.get('high')
# 		obj.save()
# 		return Response()

# class SugarViewSet(viewsets.ModelViewSet):
# 	serializer_class = SugarSerializer
# 	queryset = Sugar.objects.all()

# 	def list(self,request):
# 		patient=request.user.patient
# 		month=request.query_params.get('month')
# 		year=request.query_params.get('year')
# 		values=Sugar.objects.filter(user=patient,date__year=year,date__month=month)
# 		return Response({'sugar':SugarSerializer(values, many=True).data})

# 	def create(self,request):
# 		patient=request.user.patient
# 		value=request.data.get('value')
# 		date=request.data.get("date")
# 		date = parse(date).date()
# 		obj=Sugar(user=patient,value1=value,date=date)
# 		obj.save()
# 		return Response()

# 	def update(self, request, pk):
# 		obj=Sugar.objects.get(pk=pk)
# 		obj.value1=request.data.get('value')
# 		obj.save()
# 		return Response()

# class CholesterolViewSet(viewsets.ModelViewSet):
# 	serializer_class = CholesterolSerializer
# 	queryset = Cholesterol.objects.all()

# 	def list(self,request):
# 		patient=request.user.patient
# 		month=request.query_params.get('month')
# 		year=request.query_params.get('year')
# 		values=Cholesterol.objects.filter(user=patient,date__year=year,date__month=month)
# 		return Response({'cholesterol':CholesterolSerializer(values, many=True).data})

# 	def create(self,request):
# 		patient=request.user.patient
# 		value=request.data.get('value')
# 		date=request.data.get("date")
# 		date = parse(date).date()
# 		obj=Cholesterol(user=patient,value2=value,date=date)
# 		obj.save()
# 		return Response()

# 	def update(self, request, pk):
# 		obj=Cholesterol.objects.get(pk=pk)
# 		obj.value2=request.data.get('value')
# 		obj.save()
# 		return Response()

# class TemperatureViewSet(viewsets.ModelViewSet):
# 	serializer_class = TemperatureSerializer
# 	queryset = Temperature.objects.all()

# 	def list(self,request):
# 		patient=request.user.patient
# 		month=request.query_params.get('month')
# 		year=request.query_params.get('year')
# 		values=Temperature.objects.filter(user=patient,date__year=year,date__month=month)
# 		return Response({'temperature':TemperatureSerializer(values, many=True).data})

# 	def create(self,request):
# 		patient=request.user.patient
# 		value=request.data.get('value')
# 		date=request.data.get("date")
# 		date = parse(date).date()
# 		obj=Temperature(user=patient,value3=value,date=date)
# 		obj.save()
# 		return Response()

# 	def update(self, request, pk):
# 		obj=Temperature.objects.get(pk=pk)
# 		obj.value3=request.data.get('value')
# 		obj.save()
# 		return Response()

# class BMIViewSet(viewsets.ModelViewSet):
# 	serializer_class = BMISerializer
# 	queryset = BMI.objects.all()

# 	def list(self,request):
# 		patient=request.user.patient
# 		month=request.query_params.get('month')
# 		year=request.query_params.get('year')
# 		values=BMI.objects.filter(user=patient,date__year=year,date__month=month)
# 		return Response({'bmi':BMISerializer(values, many=True).data})

# 	def create(self,request):
# 		patient=request.user.patient
# 		value=request.data.get('value')
# 		date=request.data.get("date")
# 		date = parse(date).date()
# 		obj=BMI(user=patient,value4=value,date=date)
# 		obj.save()
# 		return Response()

# 	def update(self, request, pk):
# 		obj=BMI.objects.get(pk=pk)
# 		obj.value4=request.data.get('value')
# 		obj.save()
# 		return Response()