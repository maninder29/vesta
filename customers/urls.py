from django.conf.urls import url
from .views import *

urlpatterns = [
	url(r'^$', home, name='home'),
	url(r'^settings/$', settings, name='settings'),
	# url(r'^search/user/(?P<name>[\w.@+-]+)/$', search, name='search'),
	# url(r'^home/$', home2, name='home2'),
	# url(r'^verificationMessage/$', verification_message, name='verification_message'),
	# url(r'^patient/(?P<category>[\w\-]+)/(?P<subcategory>[\w\-]+)/$', patient_home, name='patient_home'),
	# url(r'^doctor/(?P<category>[\w\-]+)/(?P<subcategory>[\w\-]+)/$', doctor_home, name='doctor_home'),
	# url(r'^doctor/schedule/$', clinic_schedule, name='clinic_schedule'),
	# url(r'^lab/(?P<category>[\w\-]+)/(?P<subcategory>[\w\-]+)/$', lab_home, name='lab_home'),
	# url(r'^pharmacy/(?P<category>[\w\-]+)/(?P<subcategory>[\w\-]+)/$', pharmacy_home, name='pharmacy_home'),
	
	# url(r'^search/clinics/$', clinic_list, name='clinic_list'),
	# url(r'^search/doctors/$', doctor_list, name='doctor_list'),
	# url(r'^get_clinics/(?P<id>\d+)/$', get_clinics, name='get_clinics'),
	# url(r'^get_doctors/(?P<id>\d+)/$', get_doctors, name='get_doctors'),
	# url(r'^get_tests/(?P<id>\d+)/$', get_tests, name='get_tests'),
	# url(r'^search/labs/$', lab_list, name='lab_list'),
	# url(r'^search/pharmacies/$', pharmacy_list, name='pharmacy_list'),
	# url(r'^search/doctorsAndClinics/$', doctor_and_clinic_list, name='doctor_and_clinic_list'),

	# url(r'^clinic/appointment/(?P<d_id>\d+)/(?P<c_id>\d+)/$', clinic_appointment, name='clinic_appointment'),
	# url(r'^clinic/appointment/book/$', book_clinic_appointment, name='book_clinic_appointment'),
	# url(r'^clinic/appointment/cancel/(?P<id>\d+)/$', cancel_clinic_appointment, name='cancel_clinic_appointment'),
	# url(r'^clinic/appointment/offline/(?P<id>\d+)/$', offline_clinic_appointment, name='offline_clinic_appointment'),
	# url(r'^pres/delete/(?P<id>\d+)/$', prescription_delete, name='prescription_delete'),

	# url(r'^lab/appointment/select/(?P<id>\d+)/$', lab_appointment, name='lab_appointment'),
	# url(r'^lab/appointment/deactivate/(?P<id>\d+)/$', deactivate_lab_appt, name='deactivate_lab_appt'),
	# url(r'^lab/appointment/book/selected/$', book_lab_appointment, name='book_lab_appointment'),
	# url(r'^lab/appointment/cancel/(?P<id>\d+)/$', cancel_lab_appointment, name='cancel_lab_appointment'),

	# url(r'^order/cancel/(?P<id>\d+)/$', cancel_order, name='cancel_order'),
	# url(r'^order/reply/confirm/(?P<id>\d+)/$', confirm_reply, name='confirm_reply'),
	# url(r'^order/confirm/(?P<id>\d+)/$', confirm_order, name='confirm_order'),
	
	# url(r'^token/qazwsxedcrfvtgbyhn/214365/$', clinic_token_script),
	# url(r'^token/qazwsxedcrfvtgbyhn/563412/$', lab_token_script),
	# url(r'^open_report/(?P<id>\d+)/$', pdf_view, name='pdf_view'),
	# url(r'^test/$', test, name='test'),
]
