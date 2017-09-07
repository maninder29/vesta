# from collections import OrderedDict
# from dateutil.parser import parse
from django.conf import settings as SET
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.db.models import Q
# from django.forms import modelformset_factory
from django.http import Http404,JsonResponse
from django.shortcuts import render,redirect
from django.views.decorators.csrf import csrf_exempt
# from itertools import chain
# from operator import attrgetter
from PIL import Image
from pyfcm import FCMNotification
# import calendar, datetime, pandas
import geocoder, validators
from .forms import *
from .models import *
# from feedback.models import RatingForm
from . import PyOpenGraph as InfoExtractor
from posts.models import Notification, Post, WallPost
from django.utils.timesince import timesince
import pusher
from django.core.files import File

pusher_client=pusher.Pusher(app_id='303592',key='cf69569914b189660423',secret='963493a9c905d786e4d1',cluster='ap2',ssl=True)


@login_required
def home(request):
	user=request.user
	try:
		u=user.profile.patient
		return redirect('/posts/'+user.profile.setting.default_page)
	except:
		try:
			u=user.profile.doctor
			return redirect('/posts/'+user.profile.setting.default_page)
		except:
			try:
				u=user.profile.student
				return redirect('/posts/'+user.profile.setting.default_page)
			except:
				try:
					u=user.profile.fitnessenthusiast
					return redirect('/posts/'+user.profile.setting.default_page)
				except:
					form=RegisterForm(request.POST or None, request.FILES or None)
					if form.is_valid():
						name=form.cleaned_data.get('name')
						email=form.cleaned_data.get('email')
						type_of_user=form.cleaned_data.get('type_of_user')
						dp=form.cleaned_data.get('dp')
						if user.email != email:
							user.email = email
							user.save()
						try:
							profile=user.profile
							profile.dp=dp
						except:
							profile=Profile(user=user, name=name, dp=dp)
							profile.save()
						try:
							image=Image.open(dp)
							path = SET.MEDIA_ROOT+'/'+'{0}/'.format(user.email)
							if not os.path.exists(path):
								os.makedirs(path)
							w, h = image.size
							if w >h:
								diff = (w-h)/2
								image = image.crop((diff, 0, diff+h, h))
							elif h>w:
								diff = (h-w)/2
								image = image.crop((0, 0, w, w))
							resized_image = image.resize((96, 96), Image.ANTIALIAS)
							path += 'dpthumb.jpg'
							resized_image.save(path)
							local_file=open(path, 'rb')
							profile.thumbnail.save('dpthumb.jpg', File(local_file), save=True)
							local_file.close()
							os.remove(path)
						except:
							pass
						if type_of_user == 'patient':
							patient = Patient(profile=profile)
							patient.save()
							diseases=request.POST.getlist('diseases')
							for i in diseases:
								try:
									x = Disease.objects.get(name=i)
									patient.diseases.add(x)
								except:
									pass
							patient.save()
							TYPE = 'insights'
							content='Welcome! ' + name + ' to VestaSocial. Connect with other patients like yourself and give insights to others and get suggestions for your own problems.'
						elif type_of_user == 'doctor':
							doc = Doctor(profile=profile)
							doc.save()
							degrees=request.POST.getlist('degrees')
							specialities=request.POST.getlist('specialities')
							experience=request.POST.get('experience')
							for i in degrees:
								try:
									x = Degree.objects.get(name=i)
									doc.qualification.add(x)
								except:
									pass
							for i in specialities:
								try:
									x = Speciality.objects.get(name=i)
									doc.speciality.add(x)
								except:
									pass
							doc.experience = experience
							doc.save()
							TYPE = 'differential'
							content='Welcome! ' + name + ' to VestaSocial. Connect with your peers and discuss medical diagnostics. Share medical updates and discuss amongst the professional community.'
						elif type_of_user == 'student':
							stud = Student(profile=profile)
							stud.save()
							degrees=request.POST.getlist('student_degrees')
							for i in degrees:
								try:
									x = Degree.objects.get(name=i)
									stud.qualification.add(x)
								except:
									pass
							university = request.POST.get('university')
							if university != '':
								stud.university = university
							stud.save()
							TYPE = 'differential'
							content='Welcome! ' + name + ' to VestaSocial. Connect with your peers and discuss medical diagnostics. Share medical updates and discuss amongst the professional community.'
						elif type_of_user == 'fitness_enthusiast':
							enth = FitnessEnthusiast(profile=profile)
							enth.save()
							interests=request.POST.getlist('interests')
							for i in interests:
								try:
									x = Interests.objects.get(name=i)
									enth.interests.add(x)
								except:
									pass
							enth.save()
							TYPE = 'mySpace'
							content='Welcome! ' + name + ' to VestaSocial. Connect with like minded people in Healthcare. Share thoughts,motivate People and get motivated by the community.'
						else:
							return redirect('home')
						Setting(profile=profile, default_page=TYPE).save()

						pk=SET.ENV
						VESTA = Profile.objects.get(id=pk)
						WallPost( profile=VESTA, content=content, wall_profile=profile, welcome=True ).save()
						title = str(name) + " just joined VestaSocial"
						link = reverse('profile', kwargs={'id':user.id})
						key=profile.id
						for p in Profile.objects.all():
							Notification(profile=p, profile2=profile, title=title, link=link, tag='f', key=key).save()
						return redirect('home')
					context={
						'form':form,
						'interest_choices':Interests.INTEREST_CHOICES,
						'degree_choices':Degree.DEGREE_CHOICES,
						'speciality_choices':Speciality.SPECIALITY_CHOICES,
						'disease_choices':Disease.DISEASE_CHOICES
					}
					return render(request, 'initialPages/final-step.html', context)


@login_required
def settings(request):
	profile=request.user.profile
	settings=profile.setting
	if request.POST:
		default_page=request.POST.get('default_page')
		settings.default_page=default_page

		name=request.POST.get('name')
		if profile.name != name:
			profile.name=name

		phone=request.POST.get('phone')
		if not profile.phone:
			p=Phone(phone=phone)
			p.save()
			profile.phone=p
		elif profile.phone.phone != phone:
			p=profile.phone
			p.save(phone=phone)

		address=request.POST.get('address')
		if not profile.address:
			a=Address(address=address)
			g = geocoder.google(address)
			a.latitude=g.latlng[0]
			a.longitude=g.latlng[1]
			a.save()
			profile.address=a
		elif profile.address.address != address:
			a=profile.address
			a.address=address
			g = geocoder.google(address)
			a.latitude=g.latlng[0]
			a.longitude=g.latlng[1]
			a.save()
			print a.latlng

		age=request.POST.get('age')
		if profile.age != age:
			profile.age=age

		gender=request.POST.get('gender')
		if profile.gender != gender:
			profile.gender=gender

		try:
			doc = profile.doctor
			degrees=request.POST.getlist('degrees')
			doc.qualification.clear()
			for i in degrees:
				try:
					x = Degree.objects.get(name=i)
					doc.qualification.add(x)
				except:
					pass
			specialities=request.POST.getlist('specialities')
			doc.specialities.clear()
			for i in specialities:
				try:
					x = Speciality.objects.get(name=i)
					doc.speciality.add(x)
				except:
					pass
			experience=request.POST.get('experience')
			doc.experience = experience
			doc.save()
		except:
			try:
				stud = profile.student
				degrees=request.POST.getlist('student_degrees')
				stud.degrees.clear()
				for i in degrees:
					try:
						x = Degree.objects.get(name=i)
						stud.qualification.add(x)
					except:
						pass
				university = request.POST.get('university')
				if university != '':
					stud.university = university
				stud.save()
			except:
				try:
					enth = profile.fitnessenthusiast
					interests=request.POST.getlist('interests')
					enth.interests.clear()
					for i in interests:
						try:
							x = Interests.objects.get(name=i)
							enth.interests.add(x)
						except:
							pass
					enth.save()
				except:
					try:
						patient = profile.patient
						diseases=request.POST.getlist('diseases')
						patient.diseases.clear()
						for i in diseases:
							try:
								x = Disease.objects.get(name=i)
								patient.diseases.add(x)
							except:
								pass
						patient.save()
					except:
						pass
		profile.save()
		settings.save()
		return redirect('settings')
	context={
		'settings':settings,
		'interest_choices':Interests.INTEREST_CHOICES,
		'degree_choices':Degree.DEGREE_CHOICES,
		'speciality_choices':Speciality.SPECIALITY_CHOICES,
		'disease_choices':Disease.DISEASE_CHOICES
	}
	try:
		p = profile.doctor
		context['qualification'] = [ x.name for x in p.qualification.all() ]
		context['specialities'] = [ x.name for x in p.speciality.all() ]
		context['experience'] = p.experience
	except:
		try:
			p = profile.student
			context['qualification'] = [ x.name for x in p.qualification.all() ]
			context['university'] = p.university
		except:
			try:
				p = profile.fitnessenthusiast
				context['interests'] = [ x.name for x in p.interests.all() ]
			except:
				try:
					p = profile.patient
					context['diseases'] = [ x.name for x in p.diseases.all() ]
				except:
					pass
	return render(request, "social/settings.html", context)


# DEFAULT_SUB_CATEGORY = '_'

# @login_required
# def search(request, name):
# 	if request.is_ajax():
# 		name_list = name.split(' ')
# 		if len(name_list) > 1:
# 			users = User.objects.filter(Q(first_name__icontains=name_list[0]) & Q(last_name__icontains=name_list[-1]))
# 		else:
# 			users = User.objects.filter(Q(first_name__icontains=name) | Q(last_name__icontains=name))



# @login_required
# def home2(request):
# 	user=request.user
# 	try:
# 		u=user.patient
# 		return redirect(reverse('patient_home', kwargs={'category':'profile', 'subcategory':'current'}))
# 	except:
# 		try:
# 			u=user.doctor
# 			return redirect(reverse('doctor_home', kwargs={'category':'profile', 'subcategory':'appointments'}))
# 		except:
# 			try:
# 				u=user.lab
# 				return redirect(reverse('lab_home', kwargs={'category':'profile', 'subcategory':'appointments'}))
# 			except:
# 				try:
# 					u=user.pharmacy
# 					return redirect(reverse('pharmacy_home', kwargs={'category':'profile', 'subcategory':'orders'}))
# 				except:
# 					return redirect('home')


# #############################################    PATIENT    #########################################################

# @login_required
# def patient_home(request, category, subcategory):
# 	if category == 'medicalHistory' and subcategory == 'clinicSlips':
# 		return patient_history_clinic(request, category, subcategory)
# 	elif category == 'medicalHistory' and subcategory == 'labReports':
# 		return patient_history_lab(request, category, subcategory)
# 	elif category == 'medicalHistory' and subcategory == 'pharmacyOrders':
# 		return patient_history_pharmacy(request, category, subcategory)
# 	elif category == 'profile' and subcategory == 'vitals':
# 		return patient_profile_vitals(request, category, subcategory)
# 	elif category == 'profile' and subcategory == 'current':
# 		return patient_profile_current(request, category, subcategory)
# 	elif category == 'profile' and subcategory == 'pastAppointments':
# 		return patient_profile_past_appts(request, category, subcategory)
# 	elif category == 'futureAppointments' and subcategory == DEFAULT_SUB_CATEGORY:
# 		return patient_future_appts(request, category, subcategory)
# 	else:
# 		raise Http404

# @login_required
# def patient_history_clinic(request, category, subcategory):
# 	try:
# 		patient=request.user.patient
# 	except:
# 		raise Http404
# 	pres_form=PrescriptionForm(request.POST or None, request.FILES or None)
# 	result_form=ResultForm(request.POST or None, request.FILES or None)
# 	if request.FILES:
# 		if request.FILES.get('prescription'):
# 			id=request.POST.get('id')
# 			instance=ClinicSlip.objects.get(id=id)
# 			instance.prescription=request.FILES.get('prescription')
# 			instance.save()
# 			return redirect(reverse('patient_home', kwargs={'category':'medicalHistory', 'subcategory':'clinicSlips'}))
# 		elif request.FILES.get('result'):
# 			id=request.POST.get('id')
# 			instance=ClinicSlip.objects.get(id=id)
# 			result=request.FILES.get('result')
# 			obj=ClinicSlipReply(result=result).save()
# 			instance.reply_by_doctor=obj
# 			instance.save()
# 			return redirect(reverse('patient_home', kwargs={'category':'medicalHistory', 'subcategory':'clinicSlips'}))
# 	clinic_slips=ClinicSlip.objects.filter(patient=patient)


# 	# pusher_client.trigger('doctor', 'new-order', {'message': 'New order recieved'})

# 	context={
# 		'userType':'patient',
# 		'category':category,
# 		'subcategory':subcategory,
# 		'type':'normal',
# 		'object_list':clinic_slips,
# 		'pres_form':pres_form,
# 		'result_form':result_form,
# 	}
# 	return render(request, "homepage/homepage.html", context)

# @login_required
# def patient_history_lab(request, category, subcategory):
# 	try:
# 		patient=request.user.patient
# 	except:
# 		raise Http404
# 	lab_slips=LabSlip.objects.filter(patient=patient)

# 	# pusher_client.trigger('doctor', 'new-confirmed-order', {'message': 'New order confirmation'})

# 	context={
# 		'userType':'patient',
# 		'category':category,
# 		'subcategory':subcategory,
# 		'type':'normal',
# 		'object_list':lab_slips
# 	}
# 	return render(request, "homepage/homepage.html", context)

# @login_required
# def patient_history_pharmacy(request, category, subcategory):
# 	try:
# 		patient=request.user.patient
# 	except:
# 		raise Http404
# 	past_orders=PharmacyOrder.objects.filter(patient=patient, confirmed=True)
# 	context={
# 		'userType':'patient',
# 		'category':category,
# 		'subcategory':subcategory,
# 		'type':'normal',
# 		'object_list':past_orders
# 	}
# 	return render(request, "homepage/homepage.html", context)

# @login_required
# def patient_profile_vitals(request, category, subcategory):
# 	try:
# 		patient=request.user.patient
# 	except:
# 		raise Http404
# 	today=datetime.datetime.today()
# 	bp_form=BPForm(request.POST or None)
# 	if bp_form.is_valid():
# 		instance=bp_form.save(commit=False)
# 		instance.user=request.user.patient
# 		instance.date=today
# 		instance.save()
# 		return redirect(reverse('patient_home', kwargs={'category':'profile', 'subcategory':'vitals'}))

# 	sugar_form=SugarForm(request.POST or None)
# 	if sugar_form.is_valid():
# 		instance=sugar_form.save(commit=False)
# 		instance.user=request.user.patient
# 		instance.date=today
# 		instance.save()
# 		return redirect(reverse('patient_home', kwargs={'category':'profile', 'subcategory':'vitals'}))

# 	cholesterol_form=CholesterolForm(request.POST or None)
# 	if cholesterol_form.is_valid():
# 		instance=cholesterol_form.save(commit=False)
# 		instance.user=request.user.patient
# 		instance.date=today
# 		instance.save()
# 		return redirect(reverse('patient_home', kwargs={'category':'profile', 'subcategory':'vitals'}))

# 	temperature_form=TemperatureForm(request.POST or None)
# 	if temperature_form.is_valid():
# 		instance=temperature_form.save(commit=False)
# 		instance.user=request.user.patient
# 		instance.date=today
# 		instance.save()
# 		return redirect(reverse('patient_home', kwargs={'category':'profile', 'subcategory':'vitals'}))

# 	bmi_form=BMIForm(request.POST or None)
# 	if bmi_form.is_valid():
# 		instance=bmi_form.save(commit=False)
# 		instance.user=request.user.patient
# 		instance.date=today
# 		instance.save()
# 		return redirect(reverse('patient_home', kwargs={'category':'profile', 'subcategory':'vitals'}))
# 	context={
# 		'userType':'patient',
# 		'category':category,
# 		'subcategory':subcategory,
# 		'type':'normal',
# 		'bp_form':bp_form,
# 		'sugar_form':sugar_form,
# 		'cholesterol_form':cholesterol_form,
# 		'temperature_form':temperature_form,
# 		'bmi_form':bmi_form,
# 	}
# 	return render(request, "homepage/homepage.html", context)

# @login_required
# def patient_profile_current(request, category, subcategory):
# 	try:
# 		patient=request.user.patient
# 	except:
# 		raise Http404
# 	pres_form=PrescriptionForm(request.POST or None, request.FILES or None)
# 	result_form=ResultForm(request.POST or None, request.FILES or None)
# 	if request.FILES:
# 		if request.FILES.get('prescription'):
# 			id=request.POST.get('id')
# 			instance=ClinicSlip.objects.get(id=id)
# 			instance.prescription=request.FILES.get('prescription')
# 			instance.save()
# 			return redirect(reverse('patient_home', kwargs={'category':'profile', 'subcategory':'current'}))
# 		elif request.FILES.get('result'):
# 			id=request.POST.get('id')
# 			instance=ClinicSlip.objects.get(id=id)
# 			result=request.FILES.get('result')
# 			obj=ClinicSlipReply(result=result)
# 			obj.save()
# 			instance.reply_by_doctor=obj
# 			instance.save()
# 			return redirect(reverse('patient_home', kwargs={'category':'profile', 'subcategory':'current'}))
# 	clinic_slips=ClinicSlip.objects.filter(patient=patient)
# 	lab_slips=LabSlip.objects.filter(patient=patient)
# 	current=list(PharmacyOrder.objects.filter(patient=patient, confirmed=False))
# 	current_clinic_slip=clinic_slips.first()
# 	current_lab_slip=lab_slips.first()
# 	if current_clinic_slip and current_lab_slip:
# 		current.append(current_clinic_slip)
# 		current.append(current_lab_slip)
# 	elif current_clinic_slip:
# 		current.append(current_clinic_slip)
# 	elif current_lab_slip:
# 		current.append(current_lab_slip)
# 	context={
# 		'userType':'patient',
# 		'category':category,
# 		'subcategory':subcategory,
# 		'type':'normal',
# 		'object_list':current,
# 		'pres_form':pres_form,
# 		'result_form':result_form,
# 	}
# 	return render(request, "homepage/homepage.html", context)

# @login_required
# def patient_profile_past_appts(request, category, subcategory):
# 	try:
# 		patient=request.user.patient
# 	except:
# 		raise Http404
# 	today=datetime.datetime.today()
# 	past_clinic_appointments=ClinicAppointment.objects.filter(patient=patient, active=False)
# 	past_lab_appointments=LabAppointment.objects.filter(patient=patient, active=False)
# 	past_orders=PharmacyOrder.objects.filter(patient=patient, confirmed=True)
# 	past_log=sorted(
# 		chain(past_clinic_appointments,past_lab_appointments,past_orders),
# 		key=attrgetter('timestamp')
# 		)
# 	past_log.reverse()
# 	context={
# 		'userType':'patient',
# 		'category':category,
# 		'subcategory':subcategory,
# 		'type':'normal',
# 		'object_list':past_log
# 	}
# 	return render(request, "homepage/homepage.html", context)

# @login_required
# def patient_future_appts(request, category, subcategory):
# 	try:
# 		patient=request.user.patient
# 	except:
# 		raise Http404
# 	today=datetime.datetime.today()
# 	future_clinic_appointments=ClinicAppointment.objects.filter(patient=patient, date__gte=today, active=True)
# 	future_lab_appointments=LabAppointment.objects.filter(patient=patient, date__gte=today, active=True)
# 	future_appointments=sorted(
# 		chain(future_clinic_appointments,future_lab_appointments),
# 		key=attrgetter('timestamp')
# 		)
# 	context={
# 		'userType':'patient',
# 		'category':category,
# 		'subcategory':subcategory,
# 		'type':'normal',
# 		'object_list':future_appointments
# 	}
# 	return render(request, "homepage/homepage.html", context)

# #####################################################################################################################

# #################################################   DOCTOR   ########################################################

# @login_required
# def verification_message(request):
# 	return render(request, "verification_message.html", {})

# @login_required
# def doctor_home(request, category, subcategory):
# 	if category == 'patientHistory' and subcategory == DEFAULT_SUB_CATEGORY:
# 		return doctor_history(request, category, subcategory)
# 	elif category == 'profile' and subcategory == 'reports':
# 		return doctor_profile_reports(request, category, subcategory)
# 	elif category == 'profile' and subcategory == 'appointments':
# 		return doctor_profile_appointments(request, category, subcategory)
# 	else:
# 		raise Http404

# @login_required
# def doctor_history(request, category, subcategory):
# 	try:
# 		doctor=request.user.doctor
# 	except:
# 		raise Http404
# 	if not doctor.verified:
# 		return redirect('verification_message')
# 	history=ClinicSlip.objects.filter(doctor=doctor)
# 	context={
# 		'userType':'doctor',
# 		'category':category,
# 		'subcategory':subcategory,
# 		'type':'normal',
# 		'object_list':history,
# 	}
# 	return render(request, "homepage/homepage.html", context)

# @login_required
# def doctor_profile_reports(request, category, subcategory):
# 	try:
# 		doctor=request.user.doctor
# 	except:
# 		raise Http404
# 	if not doctor.verified:
# 		return redirect('verification_message')
# 	form=ConfirmationForm(request.POST or None)
# 	if form.is_valid():
# 		id=request.POST.get('id')
# 		instance=ClinicSlip.objects.get(id=id).reply_by_doctor
# 		instance.confirmed=request.POST.get('confirmed')
# 		instance.remarks=request.POST.get('remarks')
# 		instance.save()
# 		return redirect(reverse('doctor_home', kwargs={'category':'profile', 'subcategory':'reports'}))
# 	reports=ClinicSlip.objects.filter(doctor=doctor, reply_by_doctor__isnull=False, reply_by_doctor__confirmed__isnull=True)
# 	context={
# 		'userType':'doctor',
# 		'category':category,
# 		'subcategory':subcategory,
# 		'type':'normal',
# 		'reports':reports,
# 		'form':form
# 	}
# 	return render(request, "homepage/homepage.html", context)

# @login_required
# def doctor_profile_appointments(request, category, subcategory):
# 	try:
# 		doctor=request.user.doctor
# 	except:
# 		raise Http404
# 	if not doctor.verified:
# 		return redirect('verification_message')
# 	form=DiseaseForm(request.POST or None)
# 	if form.is_valid():
# 		id=request.POST.get('id')
# 		appt=ClinicAppointment.objects.get(id=id)
# 		instance=form.save(commit=False)
# 		instance.patient=appt.patient
# 		instance.doctor=doctor
# 		instance.clinic=appt.clinic
# 		instance.save()
# 		appt.active=False
# 		appt.save()
# 		return redirect(reverse('doctor_home', kwargs={'category':'profile', 'subcategory':'appointments'}))
# 	today=datetime.datetime.today()
# 	appointments=ClinicAppointment.objects.filter(doctor=doctor, date__gte=today, active=True)
# 	context={
# 		'userType':'doctor',
# 		'category':category,
# 		'subcategory':subcategory,
# 		'type':'normal',
# 		'appointments':appointments,
# 		'form':form
# 	}
# 	return render(request, "homepage/homepage.html", context)

# #####################################################################################################################

# ###################################################   LAB   #########################################################

# @login_required
# def lab_home(request, category, subcategory):
# 	if category == 'history' and subcategory == DEFAULT_SUB_CATEGORY:
# 		return lab_history(request, category, subcategory)
# 	elif category == 'profile' and subcategory == 'reports':
# 		return lab_profile_report(request, category, subcategory)
# 	elif category == 'profile' and subcategory == 'appointments':
# 		return lab_profile_appointments(request, category, subcategory)
# 	else:
# 		raise Http404

# @login_required
# def lab_history(request, category, subcategory):
# 	try:
# 		lab=request.user.lab
# 	except:
# 		raise Http404
# 	if not lab.verified:
# 		return redirect('verification_message')
# 	tests=lab.test_set.all()
# 	history=LabSlip.objects.filter(test__in=tests)
# 	context={
# 		'userType':'lab',
# 		'category':category,
# 		'subcategory':subcategory,
# 		'type':'normal',
# 		'object_list':history,
# 	}
# 	return render(request, "homepage/homepage.html", context)

# @login_required
# def lab_profile_report(request, category, subcategory):
# 	try:
# 		lab=request.user.lab
# 	except:
# 		raise Http404
# 	if not lab.verified:
# 		return redirect('verification_message')
# 	form=ResultForm(request.POST or None, request.FILES or None)
# 	if request.FILES.get('result'):
# 		id=request.POST.get('id')
# 		appt=LabAppointment.objects.get(id=id)
# 		instance=LabSlip()
# 		instance.patient=appt.patient
# 		instance.test=appt.test
# 		instance.result=request.FILES.get('result')
# 		instance.save()
# 		appt.report_generated=True
# 		appt.save()
# 		return redirect(reverse('lab_home', kwargs={'category':'profile', 'subcategory':'reports'}))
# 	tests=lab.test_set.all()
# 	reports=LabAppointment.objects.filter(test__in=tests, active=False, report_generated=False)
# 	context={
# 		'userType':'lab',
# 		'category':category,
# 		'subcategory':subcategory,
# 		'type':'normal',
# 		'reports':reports,
# 		'form':form
# 	}
# 	return render(request, "homepage/homepage.html", context)

# @login_required
# def lab_profile_appointments(request, category, subcategory):
# 	try:
# 		lab=request.user.lab
# 	except:
# 		raise Http404
# 	if not lab.verified:
# 		return redirect('verification_message')
# 	tests=lab.test_set.all()
# 	today=datetime.datetime.today()
# 	appointments=LabAppointment.objects.filter(test__in=tests, date__gte=today, active=True)
# 	context={
# 		'userType':'lab',
# 		'category':category,
# 		'subcategory':subcategory,
# 		'type':'normal',
# 		'appointments':appointments,
# 	}
# 	return render(request, "homepage/homepage.html", context)

# @login_required
# def deactivate_lab_appt(request, id):
# 	try:
# 		lab=request.user.lab
# 	except:
# 		raise Http404
# 	if not lab.verified:
# 		return redirect('verification_message')
# 	appt=LabAppointment.objects.get(id=id)
# 	if appt.test.lab == lab:
# 		appt.active=False
# 		appt.save()
# 		return redirect(reverse('lab_home', kwargs={'category':'profile', 'subcategory':'appointments'}))
# 	else:
# 		raise Http404

# #####################################################################################################################

# ################################################   PHARMACY   #######################################################

# @login_required
# def pharmacy_home(request, category, subcategory):
# 	if category == 'orderHistory' and subcategory == DEFAULT_SUB_CATEGORY:
# 		return pharmacy_history(request, category, subcategory)
# 	elif category == 'profile' and subcategory == 'confirmedOrders':
# 		return pharmacy_profile_confirmed_orders(request, category, subcategory)
# 	elif category == 'profile' and subcategory == 'orders':
# 		return pharmacy_profile_orders(request, category, subcategory)
# 	else:
# 		raise Http404

# @login_required
# def pharmacy_history(request, category, subcategory):
# 	try:
# 		pharmacy=request.user.pharmacy
# 	except:
# 		raise Http404
# 	if not pharmacy.verified:
# 		return redirect('verification_message')
# 	history=PharmacyOrder.objects.filter(pharmacy=pharmacy, confirmed=True)
# 	context={
# 		'userType':'pharmacy',
# 		'category':category,
# 		'subcategory':subcategory,
# 		'type':'normal',
# 		'history':history,
# 	}
# 	return render(request, "homepage/homepage.html", context)

# @login_required
# def pharmacy_profile_confirmed_orders(request, category, subcategory):
# 	try:
# 		pharmacy=request.user.pharmacy
# 	except:
# 		raise Http404
# 	if not pharmacy.verified:
# 		return redirect('verification_message')
# 	confirmations=PharmacyOrder.objects.filter(pharmacy=pharmacy, reply_by_pharmacy__confirmed=True, confirmed=False)
# 	context={
# 		'userType':'pharmacy',
# 		'category':category,
# 		'subcategory':subcategory,
# 		'type':'normal',
# 		'confirmations':confirmations,
# 	}
# 	return render(request, "homepage/homepage.html", context)

# @login_required
# def pharmacy_profile_orders(request, category, subcategory):
# 	try:
# 		pharmacy=request.user.pharmacy
# 	except:
# 		raise Http404
# 	if not pharmacy.verified:
# 		return redirect('verification_message')
# 	form=PharmacyOrderReplyForm(request.POST or None)
# 	if form.is_valid():
# 		instance=form.save()
# 		id=request.POST.get('id')
# 		o=PharmacyOrder.objects.get(id=id)
# 		o.reply_by_pharmacy=instance
# 		o.save()
# 		try:
# 			user=o.patient.user
# 			push_service = FCMNotification(api_key=settings.FCM_API_KEY)
# 			devices = FCMDevice.objects.filter(user=user)
# 			registration_ids=[d.registration_id for d in devices]
# 			message_title="Reply from " + str(o.pharmacy)
# 			message_body=str(instance.reply)
# 			data={
# 			"id":str(id),
# 			"message_title":str(o.pharmacy),
# 			"message_body":str(instance.reply),
# 			"tag":"pharmacy reply"
# 			}
# 			result = push_service.notify_multiple_devices(registration_ids=registration_ids, message_title=message_title, message_body=message_body, data_message=data, sound="Default", message_icon='vestapp.in/static/vesta-social-logo.png')
# 		except Exception as e:
# 			print (str(e))
# 		return redirect(reverse('pharmacy_home', kwargs={'category':'profile', 'subcategory':'orders'}))
# 	orders=PharmacyOrder.objects.filter(pharmacy=pharmacy, reply_by_pharmacy__isnull=True)
# 	context={
# 		'userType':'pharmacy',
# 		'category':category,
# 		'subcategory':subcategory,
# 		'type':'normal',
# 		'orders':orders,
# 		'form':form
# 	}
# 	return render(request, "homepage/homepage.html", context)

# #####################################################################################################################

# @login_required
# def offline_clinic_appointment(request, id):
# 	form=OfflineClinicAppointmentForm(request.POST or None)
# 	token=None
# 	if form.is_valid():
# 		instance=form.save(commit=False)
# 		doctor=request.user.doctor
# 		clinic=Clinic.objects.get(id=id)
# 		instance.doctor=doctor
# 		instance.clinic=clinic
# 		today=datetime.datetime.today()
# 		token_status=ClinicTokenStatus.objects.get(clinic=clinic, doctor=doctor, date=today)
# 		token_status.token+=1
# 		token=token_status.token
# 		instance.token=token
# 		instance.save()
# 		token_status.save()
# 		# return redirect(reverse("offline_clinic_appointment", kwargs={"id":id}))
# 	context={
# 		'form':form,
# 		'token':token
# 	}
# 	return render(request, 'offline_clinic_appointment.html', context)

# @login_required
# def clinic_schedule(request):
# 	try:
# 		doctor=request.user.doctor
# 	except:
# 		raise Http404
# 	queryset=ClinicSchedule.objects.filter(doctor=doctor)
# 	if queryset:
# 		ClinicScheduleFormset = modelformset_factory(ClinicSchedule, form=ClinicScheduleForm, extra=0)
# 	else:
# 		ClinicScheduleFormset = modelformset_factory(ClinicSchedule, form=ClinicScheduleForm)
# 	formset = ClinicScheduleFormset(request.POST or None, queryset=queryset)
# 	if formset.is_valid():
# 		print("valid")
# 		for form in formset:
# 			obj = form.save(commit=False)
# 			if form.cleaned_data:
# 				obj.save()
# 		return redirect('clinic_schedule')
# 	return render(request, "clinic_schedule.html", {"formset": formset})

# @login_required
# def clinic_appointment(request, d_id, c_id):
# 	doctor=Doctor.objects.get(id=d_id)
# 	clinic=Clinic.objects.get(id=c_id)
# 	today=datetime.datetime.today()
# 	date_list = pandas.date_range(today,today+datetime.timedelta(days=5), freq="D").date
# 	date_token_list={}
# 	for date in date_list:
# 		week_day=calendar.day_name[date.weekday()]
# 		try:
# 			schedules=ClinicSchedule.objects.filter(doctor=doctor,clinic=clinic,day=week_day)
# 			try:
# 				token=ClinicTokenStatus.objects.get(doctor=doctor, clinic=clinic, date=date).token
# 			except Exception as e:
# 				# print e
# 				t=ClinicTokenStatus(doctor=doctor, clinic=clinic, date=date)
# 				t.save()
# 				token=0
# 			if token<schedules.first().max_token: # 1 DAY -> 1 MAX_TOKEN
# 				date_token_list[date]=schedules
# 		except:
# 			pass
# 	# print date_token_list
# 	context={
# 		'doctor':doctor,
# 		'clinic':clinic,
# 		'date_token_list':OrderedDict(sorted(date_token_list.items(), key=lambda t: t[0])),
# 	}
# 	return render(request, "homepage/clinic-time-slots.html",context)

# @login_required
# def book_clinic_appointment(request):
# 	if request.method=='POST':
# 		try:
# 			patient=request.user.patient
# 		except:
# 			raise Http404
# 		doctor_id=request.POST.get("doctor")
# 		doctor=Doctor.objects.get(id=doctor_id)
# 		clinic_id=request.POST.get("clinic")
# 		clinic=Clinic.objects.get(id=clinic_id)
# 		sch_id=request.POST.get('sch')
# 		sch=ClinicSchedule.objects.get(id=sch_id)
# 		date=request.POST.get("date")
# 		date = parse(date).date()
# 		t=ClinicTokenStatus.objects.get(doctor=doctor, clinic=clinic, date=date)
# 		t.token+=1
# 		token_no=t.token
# 		today=datetime.datetime.now()
# 		current_time=today.time()
# 		time = (datetime.datetime.combine(date,sch.start)+datetime.timedelta(minutes=3*(token_no-1))).time()
# 		if date == today.date() and datetime.datetime.combine(date,time)<datetime.datetime.combine(date,current_time):
# 			time=(datetime.datetime.combine(date,current_time)+datetime.timedelta(minutes=15)).time()
# 		appointment=ClinicAppointment(
# 			patient=patient,
# 			doctor=doctor,
# 			clinic=clinic,
# 			date=date,
# 			time=time,
# 			token=token_no
# 			).save()
# 		t.save()
# 		context={
# 			'doctor':doctor.user.get_full_name(),
# 			'clinic':clinic.name,
# 			'date':date,
# 			'time':time,
# 			'token':token_no,
# 			'sch':sch,
# 			'type':'c'
# 		}
# 		return render(request, "homepage/appointment_success.html", context)
# 	else:
# 		raise Http404

# @login_required
# def cancel_clinic_appointment(request, id):
# 	try:
# 		patient=request.user.patient
# 	except:
# 		raise Http404
# 	a=ClinicAppointment.objects.get(id=id)
# 	if a.patient == patient:
# 		a.delete()
# 		return redirect(reverse('patient_home', kwargs={'category':'futureAppointments', 'subcategory':'_'}))
# 	else:
# 		raise Http404

# @login_required
# def lab_appointment(request, id):
# 	test=Test.objects.get(id=id)
# 	lab=test.lab
# 	today=datetime.datetime.today()
# 	date_list = pandas.date_range(today,today+datetime.timedelta(days=5), freq="D").date
# 	date_token_list={}
# 	for date in date_list:
# 		week_day=calendar.day_name[date.weekday()]
# 		try:
# 			schedules=LabSchedule.objects.filter(test=test, day=week_day)
# 			try:
# 				token=LabTokenStatus.objects.get(test=test, date=date).token
# 			except:
# 				l=LabTokenStatus(test=test, date=date)
# 				l.save()
# 				token=0
# 			if token<schedules.first().max_token:
# 				date_token_list[date]=schedules
# 		except:
# 			pass
		
# 	context={
# 		'lab':lab,
# 		'test':test,
# 		'date_token_list':OrderedDict(sorted(date_token_list.items(), key=lambda t: t[0])),
# 	}
# 	return render(request, "homepage/lab-time-slots.html",context)

# @login_required
# def book_lab_appointment(request):
# 	if request.method=='POST':
# 		try:
# 			patient=request.user.patient
# 		except:
# 			raise Http404
# 		test_id=request.POST.get("id")
# 		test=Test.objects.get(id=test_id)
# 		lab=test.lab
# 		sch_id=request.POST.get('sch')
# 		sch=LabSchedule.objects.get(id=sch_id)
# 		date=request.POST.get("date")
# 		date = parse(date).date()
# 		t=LabTokenStatus.objects.get(test=test, date=date)
# 		t.token+=1
# 		token_no=t.token
# 		today=datetime.datetime.now()
# 		current_time=today.time()
# 		time = (datetime.datetime.combine(date,sch.start)+datetime.timedelta(minutes=10*(token_no-1))).time()
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
# 			'lab':lab.user.get_full_name(),
# 			'test':test.name,
# 			'date':date,
# 			'time':time,
# 			'token':token_no,
# 			'sch':sch,
# 			'type':'l'
# 		}
# 		return render(request, "homepage/appointment_success.html", context)
# 	else:
# 		raise Http404

# @login_required
# def cancel_lab_appointment(request, id):
# 	try:
# 		patient=request.user.patient
# 	except:
# 		raise Http404
# 	a=LabAppointment.objects.get(id=id)
# 	if a.patient == patient:
# 		a.delete()
# 		return redirect(reverse('patient_home', kwargs={'category':'futureAppointments', 'subcategory':'_'}))
# 	else:
# 		raise Http404

# @login_required
# def confirm_order(request, id):
# 	try:
# 		pharmacy=request.user.pharmacy
# 	except:
# 		raise Http404
# 	if not pharmacy.verified:
# 		return redirect('verification_message')
# 	o=PharmacyOrder.objects.get(id=id)
# 	if o.pharmacy == pharmacy:
# 		o.confirmed=True
# 		o.save()
# 		try:
# 			user=o.patient.user
# 			push_service = FCMNotification(api_key=settings.FCM_API_KEY)
# 			devices = FCMDevice.objects.filter(user=user)
# 			registration_ids=[d.registration_id for d in devices]
# 			message_title="Reply from " + str(o.pharmacy)
# 			message_body="Your order has been confirmed."
# 			data={
# 				"id":str(id),
# 				"message_title":"Reply from " + str(o.pharmacy),
# 				"message_body":"Your order has been confirmed.",
# 				"tag":"pharmacy confirm"
# 				}
# 			result = push_service.notify_multiple_devices(registration_ids=registration_ids, message_title=message_title, message_body=message_body, data_message=data, sound="Default", message_icon='vestapp.in/static/vesta-social-logo.png')
# 		except Exception as e:
# 			print (str(e))
# 		return redirect(reverse('pharmacy_home', kwargs={'category':'profile', 'subcategory':'confirmedOrders'}))
# 	else:
# 		raise Http404

# @login_required
# def clinic_token_script(request):
# 	# doctors=Doctor.objects.all()
# 	# today=datetime.datetime.today()
# 	# date_list = pandas.date_range(today,today+datetime.timedelta(days=20), freq="D").date
# 	# for d in doctors:
# 	# 	clinics=d.clinic.all()
# 	# 	for c in clinics:
# 	# 		for day in date_list:
# 	# 			t=ClinicTokenStatus(doctor=d, clinic=c, date=day)
# 	# 			t.save()
# 	# 			print(str(d)+" "+str(c)+" "+str(day))

# 	# return redirect("/")
# 	raise Http404

# @login_required
# def lab_token_script(request):
# 	# tests=Test.objects.all()
# 	# today=datetime.datetime.today()
# 	# date_list = pandas.date_range(today,today+datetime.timedelta(days=20), freq="D").date
# 	# for t in tests:
# 	# 	for day in date_list:
# 	# 		l=LabTokenStatus(test=t, date=day)
# 	# 		l.save()
# 	# 		print(str(t)+str(day))
# 	# return redirect("/")
# 	raise Http404

# @login_required
# def doctor_list(request):
# 	query=request.GET.get("q")
# 	form=RatingForm(request.POST or None)
# 	if request.method=='POST' and form.is_valid():
# 		id=int(request.POST.get('user'))
# 		user = User.objects.get(id=id)
# 		reviewer = request.user
# 		instance = Rating.objects.filter(user=user, reviewer=reviewer)
# 		if instance.exists():
# 			instance=instance.first()
# 			instance.value=int(request.POST.get('value'))
# 			instance.content=request.POST.get('content')
# 		else:
# 			instance=form.save(commit=False)
# 			instance.user = user
# 			instance.reviewer = reviewer
# 		instance.save()
# 		return redirect(reverse('doctor_list')+"?q="+query)
# 	if query:
# 		doctors=Doctor.objects.filter(
# 			Q(profile__user__username__icontains=query)|
# 			Q(profile__user__first_name__icontains=query)|
# 			Q(profile__user__last_name__icontains=query) |
# 			Q(qualification__icontains=query)|
# 			Q(speciality__icontains=query)|
# 			Q(profile__tags__name__icontains=query)
# 		).distinct()
# 	else:
# 		doctors=Doctor.objects.all()
# 	context={
# 		"doctors":doctors,
# 		'type':'d'
# 	}
# 	return render(request, "homepage/searchResults.html", context)

# @login_required
# def get_clinics(request, id):
# 	if request.is_ajax():
# 		doctor=Doctor.objects.get(id=id)
# 		listt = []
# 		for i in doctor.clinic.all():
# 			dictionary = {
# 				'dp': str(i.dp_url),
# 				'name' : i.name,
# 				'address' : i.address.address,
# 				'fees' : str(DoctorFee.objects.get(doctor=doctor, clinic=i).fees),
# 				'schedule': "1pm - 4pm",
# 				'link': reverse('clinic_appointment', kwargs = {'d_id' : doctor.id, 'c_id' : i.id})
# 			}
# 			listt.append(dictionary)
# 		return JsonResponse({'clinics' : listt})
# 	else:
# 		return redirect('doctor_list')

# @login_required
# def get_doctors(request, id):
# 	if request.is_ajax():
# 		clinic=Clinic.objects.get(id=id)
# 		listt = []
# 		for i in clinic.doctor_set.all():
# 			dictionary = {
# 				'dp': str(i.dp_url),
# 				'name' : i.user.get_full_name(),
# 				'speciality' : i.speciality,
# 				'fees' : str(DoctorFee.objects.get(doctor=i, clinic=clinic).fees),
# 				'schedule': "1pm - 4pm",
# 				'link': reverse('clinic_appointment', kwargs = {'d_id' : i.id, 'c_id' : clinic.id})
# 			}
# 			listt.append(dictionary)
# 		return JsonResponse({'doctors' : listt})
# 	else:
# 		return redirect('clinic_list')

# @login_required
# def get_tests(request, id):
# 	if request.is_ajax():
# 		lab=Lab.objects.get(id=id)
# 		listt = []
# 		for i in lab.test_set.all():
# 			dictionary = {
# 				'name' : i.name,
# 				'fees' : str(i.fees),
# 				'link': reverse('lab_appointment', kwargs = {'id' : i.id})
# 			}
# 			listt.append(dictionary)
# 		return JsonResponse({'tests' : listt})
# 	else:
# 		return redirect('lab_list')

# @login_required
# def clinic_list(request):
# 	query=request.GET.get("q")
# 	if query:
# 		clinics=Clinic.objects.filter(
# 			Q(is_active=True)&(
# 			Q(name__icontains=query)|
# 			Q(tags__name__icontains=query))
# 		).distinct()
# 	else:
# 		clinics=Clinic.objects.filter(is_active=True)
# 	context={
# 		"clinics":clinics,
# 		'type':'c'
# 	}
# 	return render(request, "homepage/searchResults.html", context)

# @login_required
# def doctor_and_clinic_list(request):
# 	query=request.GET.get("q")
# 	form=RatingForm(request.POST or None)
# 	if request.method=='POST' and form.is_valid():
# 		id=int(request.POST.get('user'))
# 		user = User.objects.get(id=id)
# 		reviewer = request.user
# 		instance = Rating.objects.filter(user=user, reviewer=reviewer)
# 		if instance.exists():
# 			instance=instance.first()
# 			instance.value=int(request.POST.get('value'))
# 			instance.content=request.POST.get('content')
# 		else:
# 			instance=form.save(commit=False)
# 			instance.user = user
# 			instance.reviewer = reviewer
# 		instance.save()
# 		return redirect(reverse('doctor_and_clinic_list')+"?q="+query)
# 	clinics=Clinic.objects.filter(Q(is_active=True)&Q(tags__name__icontains=query)).distinct()
# 	doctors=Doctor.objects.filter(
# 			Q(speciality__icontains=query)|
# 			Q(tags__name__icontains=query)
# 		).distinct()
# 	# queryset=list(clinics)+list(doctors)
# 	context={
# 		"clinics":clinics,
# 		"doctors":doctors,
# 		'type':'cd'
# 	}
# 	return render(request, "homepage/searchResults.html", context)

# from math import radians, cos, sin, asin, sqrt
# def haversine(lon1, lat1, lon2, lat2):
# 	lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
# 	dlon = lon2 - lon1 
# 	dlat = lat2 - lat1 
# 	a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
# 	c = 2 * asin(sqrt(a)) 
# 	km = 6367 * c
# 	return km

# @login_required
# def pharmacy_list(request):
# 	query=request.GET.get("q")
# 	if query:
# 		pharmacies=Pharmacy.objects.filter(
# 			Q(profile__user__username__icontains=query)|
# 			Q(profile__user__first_name__icontains=query)|
# 			Q(profile__user__last_name__icontains=query) |
# 			Q(profile__tags__name__icontains=query)
# 		).distinct()
# 	else:
# 		pharmacies=Pharmacy.objects.all()

# 	a = request.user.profile.address
# 	if a:
# 		distances = [haversine(float(a.longitude), float(a.latitude), float(p.address.longitude), float(p.address.latitude)) for p in pharmacies]
# 		pharmacies = [x for (y,x) in sorted(zip(distances, pharmacies))]

# 	rating_form=RatingForm(request.POST or None)
# 	if request.method=='POST' and rating_form.is_valid():
# 		id=int(request.POST.get('user'))
# 		user = User.objects.get(id=id)
# 		reviewer = request.user
# 		instance = Rating.objects.filter(user=user, reviewer=reviewer)
# 		if instance.exists():
# 			instance=instance.first()
# 			instance.value=int(request.POST.get('value'))
# 			instance.content=request.POST.get('content')
# 		else:
# 			instance=rating_form.save(commit=False)
# 			instance.user = user
# 			instance.reviewer = reviewer
# 		instance.save()
# 		return redirect(reverse('pharmacy_list')+"?q="+query)
	# form=PharmacyOrderForm(request.POST or None, request.FILES or None)
	# if request.method=='POST' and form.is_valid():
	# 	try:
	# 		patient=request.user.patient
	# 	except:
	# 		raise Http404
	# 	instance=PharmacyOrder()
	# 	instance.patient=patient
	# 	pk=request.POST.get('id')
	# 	pharmacy=Pharmacy.objects.get(id=pk)
	# 	instance.pharmacy=pharmacy
	# 	instance.remarks=request.POST.get('remarks')
	# 	instance.prescription=request.FILES.get('prescription')
	# 	instance.save()

	# 	pusher_client.trigger(pharmacy.user.username, 'new-order', {})
		
	# 	address=request.POST.get('address')
	# 	add=patient.address
	# 	if not add:
	# 		add=Address()
	# 		add.address=address
	# 		try:
	# 			g=geocoder.google(address)
	# 			add.latitude=g.latlng[0]
	# 			add.longitude=g.latlng[1]
	# 		except:
	# 			pass
	# 		add.save()
	# 		patient.address=add
	# 	elif add.address != address:
	# 		add.address=address
	# 		try:
	# 			g=geocoder.google(address)
	# 			add.latitude=g.latlng[0]
	# 			add.longitude=g.latlng[1]
	# 		except:
	# 			pass
	# 		add.save()
	# 	ph=patient.phone
	# 	phone=request.POST.get('phone')
	# 	if not ph:
	# 		ph=Phone()
	# 		ph.phone=phone
	# 		ph.save()
	# 		patient.phone=ph
	# 	elif ph.phone != phone:
	# 		ph.phone=phone
	# 		ph.save()
	# 	patient.save()
	# 	return redirect(reverse('patient_home', kwargs={'category':'profile', 'subcategory':'current'}))
	# context={
	# 	"pharmacies":pharmacies,
	# 	# "form":form,
	# 	'type':'p'
	# }	
	# return render(request, "homepage/searchResults.html",context)

# @login_required
# def cancel_order(request, id):
# 	try:
# 		patient=request.user.patient
# 	except:
# 		raise Http404
# 	o=PharmacyOrder.objects.get(id=id)
# 	if o.patient == patient:
# 		if not o.confirmed:
# 			o.delete()
# 		else:
# 			message = "Order is already confirmed. Contact pharmacy for further details."
# 		return redirect(reverse('patient_home', kwargs={'category':'profile', 'subcategory':'current'}))
# 	else:
# 		raise Http404

# @login_required
# def confirm_reply(request, id):
# 	try:
# 		patient=request.user.patient
# 	except:
# 		raise Http404
# 	order=PharmacyOrder.objects.get(id=id)
# 	if order.patient == patient:
# 		r=order.reply_by_pharmacy
# 		r.confirmed=True
# 		r.save()

# 		pusher_client.trigger(order.pharmacy.user.username, 'new-confirmed-order', {})

# 		return redirect(reverse('patient_home', kwargs={'category':'profile', 'subcategory':'current'}))
# 	else:
# 		raise Http404

# @login_required
# def lab_list(request):
# 	query=request.GET.get("q")
# 	form=RatingForm(request.POST or None)
# 	if request.method=='POST' and form.is_valid():
# 		id=int(request.POST.get('user'))
# 		user = User.objects.get(id=id)
# 		reviewer = request.user
# 		instance = Rating.objects.filter(user=user, reviewer=reviewer)
# 		if instance.exists():
# 			instance=instance.first()
# 			instance.value=int(request.POST.get('value'))
# 			instance.content=request.POST.get('content')
# 		else:
# 			instance=form.save(commit=False)
# 			instance.user = user
# 			instance.reviewer = reviewer
# 		instance.save()
# 		return redirect(reverse('lab_list')+"?q="+query)
# 	if query:
# 		labs=Lab.objects.filter(
# 			Q(profile__user__username__icontains=query)|
# 			Q(profile__user__first_name__icontains=query)|
# 			Q(profile__user__last_name__icontains=query) |
# 			Q(profile__tags__name__icontains=query)|
# 			Q(test__name__icontains=query)
# 		).distinct()
# 	else:
# 		labs=Lab.objects.all()
# 	context={
# 		"labs":labs,
# 		'type':'l'
# 	}
# 	return render(request, "homepage/searchResults.html", context)


# @login_required
# def prescription_delete(request, id=None):
# 	instance = ClinicSlip.objects.get(id=id)
# 	instance.prescription=None
# 	instance.save()
# 	return redirect('patient_profile')


# def pdf_view(request, id):
# 	report=LabSlip.objects.get(id=id).result
# 	with open("D:\\venv\\vesta\\static\\media_root\\reports\\sample.pdf", 'rb') as pdf:
# 		response = HttpResponse(pdf.read(), content_type='application/pdf')
# 		response['Content-Disposition'] = 'inline;filename=some_file.pdf'
# 		return response
# 	pdf.closed

@csrf_exempt
def thumbnail(request):
	text = request.POST.get('text')
	text = text.split('http')
	result = ''

	if len(text) == 1:
		return JsonResponse({'match' : 'false'})

	else:
		text = text[1]
		text = text.split(" ")
		url = "http" + str(text[0])


		if validators.url(url):
			try:
				data = InfoExtractor.PyOpenGraph(url)
				return JsonResponse({'data' : data.metadata, 'match' : 'true'})

			except:
				return JsonResponse({'match' : 'false'})

		else:
			return JsonResponse({'match' : 'false'})
