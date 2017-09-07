from rest_framework import serializers
from customers.models import *
from django.contrib.auth.models import User

# self -> serialzer
# instance -> model

class UserSerializer(serializers.ModelSerializer):
	id=serializers.SerializerMethodField()
	def get_id(self, instance):
		try:
			return instance.profile.id
		except:
			return "null"
	dp=serializers.SerializerMethodField()
	def get_dp(self, instance):
		try:
			return instance.profile.thumbnail_url
		except:
			return "/static/img/default-thumbnail.jpg"
	user_type=serializers.SerializerMethodField()
	def get_user_type(self, instance):
		try:
			x=instance.profile.patient
			return "patient"
		except:
			try:
				x=instance.profile.doctor
				return "doctor"
			except:
				try:
					x=instance.profile.student
					return "student"
				except:
					try:
						x=instance.profile.fitnessenthusiast
						return "fitness_enthusiast"
					except:
						return "null"
	social_name=serializers.SerializerMethodField()
	def get_social_name(self, instance):
		return instance.get_full_name()
	name=serializers.SerializerMethodField()
	def get_name(self, instance):
		try:
			return instance.profile.name
		except:
			return "null"
	class Meta:
		model = User
		fields = ['name', 'social_name', 'email', 'dp', 'id', 'user_type', 'username']


class ProfileSerializer(serializers.ModelSerializer):
	dp=serializers.SerializerMethodField()
	def get_dp(self, instance):
		try:
			return instance.thumbnail_url
		except:
			return "/static/img/default-thumbnail.jpg"
	user_type=serializers.SerializerMethodField()
	def get_user_type(self, instance):
		try:
			x=instance.patient
			return "patient"
		except:
			try:
				x=instance.doctor
				return "doctor"
			except:
				try:
					x=instance.student
					return "student"
				except:
					try:
						x=instance.fitnessenthusiast
						return "fitness_enthusiast"
					except:
						return "null"
	class Meta:
		model=Profile
		fields = [ 'id', 'name', 'dp', 'vip', 'user_type' ]

class AddressSerializer(serializers.ModelSerializer):
	class Meta:
		model = Address
		fields = ['address','latitude','longitude']
	

class FCMDeviceSerializer(serializers.ModelSerializer):
	profile=ProfileSerializer()
	class Meta:
		model = FCMDevice
		fields = ['registration_id','profile']


# class ClinicSerializer(serializers.ModelSerializer):
# 	address=AddressSerializer()
# 	phone=serializers.SerializerMethodField()
# 	def get_phone(self,instance):
# 		return str(instance.phone)
# 	dp=serializers.SerializerMethodField()
# 	def get_dp(self, instance):
# 		return instance.dp_url()
# 	class Meta:
# 		model = Clinic
# 		fields = ['id','name','address','phone','dp']

# class DetailedClinicSerializer(serializers.ModelSerializer):
# 	doctors=serializers.SerializerMethodField()
# 	def get_doctors(self, instance):
# 		doctors=Doctor.objects.filter(clinic=instance)
# 		doctor_list=[]
# 		for d in doctors:
# 			schedule=ClinicSchedule.objects.filter(clinic=instance, doctor=d)
# 			try:
# 				fee=DoctorFee.objects.get(doctor=d,clinic=instance).fees
# 			except:
# 				fee='unknown'
# 			record={
# 				'id':d.id,
# 				'name':d.user.get_full_name(),
# 				'qualification':d.qualification,
# 				'experience':d.experience,
# 				'fee':fee,
# 				'dp':d.dp_url,
# 				'schedule':ClinicScheduleSerializer(schedule,many=True).data
# 			}
# 			doctor_list.append(record)
# 		return doctor_list
# 	class Meta:
# 		model = Clinic
# 		fields = ['name','doctors']


# class LabSerializer(serializers.ModelSerializer):
# 	user=UserSerializer()
# 	address=AddressSerializer()
# 	phone=serializers.SerializerMethodField()
# 	def get_phone(self,instance):
# 		return str(instance.phone)
# 	dp=serializers.SerializerMethodField()
# 	def get_dp(self,instance):
# 		return instance.dp_url
# 	class Meta:
# 		model = Lab
# 		fields = ['id','user','address','phone','dp']


# class TestSerializer(serializers.ModelSerializer):
# 	schedule=serializers.SerializerMethodField()
# 	def get_schedule(self,instance):
# 		schedule=LabSchedule.objects.filter(test=instance)
# 		return LabScheduleSerializer(schedule,many=True).data
# 	class Meta:
# 		model = Test
# 		fields = ['id','name','fees','schedule']


# class PatientSerializer(serializers.ModelSerializer):
# 	user=UserSerializer()
# 	address=AddressSerializer()
# 	phone=serializers.SerializerMethodField()
# 	def get_phone(self,instance):
# 		return str(instance.phone)
# 	dp=serializers.SerializerMethodField()
# 	def get_dp(self,instance):
# 		return instance.dp_url
# 	class Meta:
# 		model = Patient
# 		fields = ['user','phone','address','gender','age','dp']

	
# class DoctorSerializer(serializers.ModelSerializer):
# 	user=UserSerializer()
# 	# clinic=ClinicSerializer(read_only=True, many=True)
# 	phone=serializers.SerializerMethodField()
# 	def get_phone(self,instance):
# 		return str(instance.phone)
# 	dp=serializers.SerializerMethodField()
# 	def get_dp(self,instance):
# 		return instance.dp_url
# 	class Meta:
# 		model = Doctor
# 		fields = ['id','user','phone','gender','qualification','experience','dp']

	

# class DoctorFeesSerializer(serializers.ModelSerializer):
# 	doctor=serializers.PrimaryKeyRelatedField(queryset=Doctor.objects.all())
# 	clinic=serializers.PrimaryKeyRelatedField(queryset=Clinic.objects.all())
# 	class Meta:
# 		model = DoctorFee
# 		fields = ['doctor','clinic','fees']


# class ClinicScheduleSerializer(serializers.ModelSerializer):
# 	# doctor=serializers.PrimaryKeyRelatedField(queryset=Doctor.objects.all())
# 	# clinic=serializers.PrimaryKeyRelatedField(queryset=Clinic.objects.all())
# 	class Meta:
# 		model = ClinicSchedule
# 		fields = ['day','start','end']

# class AdvancedClinicScheduleSerializer(serializers.ModelSerializer):
# 	# doctor=serializers.PrimaryKeyRelatedField(queryset=Doctor.objects.all())
# 	# clinic=serializers.PrimaryKeyRelatedField(queryset=Clinic.objects.all())
# 	class Meta:
# 		model = ClinicSchedule
# 		fields = ['id','start','end']


# class LabScheduleSerializer(serializers.ModelSerializer):
# 	# lab=serializers.PrimaryKeyRelatedField(queryset=Lab.objects.all())
# 	class Meta:
# 		model = LabSchedule
# 		fields = ['day','start','end']

# class AdvancedLabScheduleSerializer(serializers.ModelSerializer):
# 	# lab=serializers.PrimaryKeyRelatedField(queryset=Lab.objects.all())
# 	class Meta:
# 		model = LabSchedule
# 		fields = ['id','start','end']


# class ClinicAppointmentSerializer(serializers.ModelSerializer):
# 	clinic=serializers.SerializerMethodField()
# 	def get_clinic(instance,self):
# 		return {'id':str(self.clinic.id),'name':str(self.clinic),'phone':str(self.clinic.phone),'address':AddressSerializer(self.clinic.address).data}

# 	doctor=serializers.SerializerMethodField()
# 	def get_doctor(instance,self):
# 		try:
# 			fee=DoctorFee.objects.get(doctor=self.doctor, clinic=self.clinic).fees
# 		except:
# 			fee="unknown"
# 		return {'id':str(self.doctor.id),'name':str(self.doctor.user.get_full_name()),'fees':str(fee),'dp':str(self.doctor.dp_url)}
# 	class Meta:
# 		model = ClinicAppointment
# 		fields = ['id','doctor','clinic','date','time','token','query']


# class LabAppointmentSerializer(serializers.ModelSerializer):
# 	test=serializers.SerializerMethodField()
# 	def get_test(instance,self):
# 		t=self.test
# 		return {
# 			'id':str(t.id),
# 			'lab_id':str(t.lab.id),
# 			'name':str(t.name),
# 			'fees':str(t.fees),
# 			'lab':str(t.lab),
# 			'phone':str(t.lab.phone),
# 			'dp':str(t.lab.dp_url),
# 			'address':AddressSerializer(self.test.lab.address).data
# 		}
# 	class Meta:
# 		model = LabAppointment
# 		fields = ['id','test','date','time','token']


# class ClinicTokenStatusSerializer(serializers.ModelSerializer):
# 	clinic=serializers.SerializerMethodField()
# 	def get_clinic(instance,self):
# 		return {'name':str(self.clinic), 'phone':str(self.clinic.phone)}

# 	doctor=serializers.SerializerMethodField()
# 	def get_doctor(instance,self):
# 		try:
# 			fee=DoctorFee.objects.get(doctor=self.doctor, clinic=self.clinic).fees
# 		except:
# 			fee="unknown"
# 		return {'id':str(self.doctor.id),'name':str(self.doctor.user.get_full_name()),'fees':fee}
# 	class Meta:
# 		model = ClinicTokenStatus
# 		fields = ['id','clinic','doctor','date','token']


# class LabTokenStatusSerializer(serializers.ModelSerializer):
# 	lab=serializers.PrimaryKeyRelatedField(queryset=Lab.objects.all())
# 	class Meta:
# 		model = LabTokenStatus
# 		fields = ['id','lab','date','token']


# class ClinicSlipSerializer(serializers.ModelSerializer):
# 	clinic=serializers.SerializerMethodField()
# 	def get_clinic(instance,self):
# 		return {'id':str(self.clinic.id),'name':str(self.clinic),'phone':str(self.clinic.phone)}

# 	doctor=serializers.SerializerMethodField()
# 	def get_doctor(instance,self):
# 		try:
# 			fee=DoctorFee.objects.get(doctor=self.doctor, clinic=self.clinic).fees
# 		except:
# 			fee='unknown'
# 		return {'id':str(self.doctor.id),'name':str(self.doctor.user.get_full_name()),'fees':str(fee),'dp':str(self.doctor.dp_url)}

# 	reply_by_doctor=serializers.SerializerMethodField()
# 	def get_reply_by_doctor(instance, self):
# 		if self.reply_by_doctor:
# 			if self.reply_by_doctor.confirmed:
# 				re='Yes'
# 			else:
# 				re='No'

# 			if self.reply_by_doctor.remarks:
# 				remarks=str(self.reply_by_doctor.remarks)
# 			else:
# 				remarks='None'
# 		else:
# 			re='Not yet confirmed'
# 			remarks='None'
# 		return {'re-appointment':re, 'remarks':remarks}
# 	class Meta:
# 		model = ClinicSlip
# 		fields = ['id','doctor','clinic','disease_name','prescription','timestamp','reply_by_doctor']


# class LabSlipSerializer(serializers.ModelSerializer):
# 	lab=serializers.SerializerMethodField()
# 	def get_lab(instance,self):
# 		return {'id':str(self.test.lab.id),'name':str(self.test.lab),'phone':str(self.test.lab.phone),'test_name':str(self.test.name),'fees':str(self.test.fees),'dp':str(self.test.lab.dp_url)}
# 	class Meta:
# 		model = LabSlip
# 		fields = ['id','test','result','timestamp','lab']


# class PharmacyOrderSerializer(serializers.ModelSerializer):
# 	pharmacy=serializers.SerializerMethodField()
# 	def get_pharmacy(self,instance):
# 		p=instance.pharmacy
# 		return {'id':str(p.id),'name':str(p),'phone':str(p.phone),'address':AddressSerializer(p.address).data,'dp':str(p.dp_url)}
# 	reply_by_pharmacy=serializers.SerializerMethodField()
# 	def get_reply_by_pharmacy(self,instance):
# 		if instance.reply_by_pharmacy:
# 			return str(instance.reply_by_pharmacy.reply)
# 		else:
# 			return ""
# 	class Meta:
# 		model = PharmacyOrder
# 		fields = ['id','pharmacy','prescription','remarks','timestamp','reply_by_pharmacy','confirmed']


# class PharmacySerializer(serializers.ModelSerializer):
# 	user=UserSerializer()
# 	address=AddressSerializer()
# 	phone=serializers.SerializerMethodField()
# 	def get_phone(self,instance):
# 		return str(instance.phone)
# 	dp=serializers.SerializerMethodField()
# 	def get_dp(self,instance):
# 		return instance.dp_url
# 	class Meta:
# 		model = Pharmacy
# 		fields = ['id','user','address','dp','phone']

# class PharmacyOrderReplySerializer(serializers.ModelSerializer):
# 	class Meta:
# 		model = PharmacyOrderReply
# 		fields = '__all__'

# class BloodPressureSerializer(serializers.ModelSerializer):
# 	def get_name(instance,self):
# 		return "bp"
# 	class Meta:
# 		model=BloodPressure
# 		fields=['id','date','high','low']

# class SugarSerializer(serializers.ModelSerializer):
# 	def get_name(instance,self):
# 		return "sugar"
# 	class Meta:
# 		model=Sugar
# 		fields=['id','date','value1']

# class CholesterolSerializer(serializers.ModelSerializer):
# 	def get_name(instance,self):
# 		return "cholesterol"
# 	class Meta:
# 		model=Cholesterol
# 		fields=['id','date','value2']

# class TemperatureSerializer(serializers.ModelSerializer):
# 	def get_name(instance,self):
# 		return "temperature"
# 	class Meta:
# 		model=Temperature
# 		fields=['id','date','value3']

# class BMISerializer(serializers.ModelSerializer):
# 	def get_name(instance,self):
# 		return "bmi"
# 	class Meta:
# 		model=BMI
# 		fields=['id','date','value4']
