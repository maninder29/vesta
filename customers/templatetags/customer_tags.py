from django import template
from customers.models import *
from datetime import datetime
import calendar, random
from friendship.models import *
from posts.models import *
from feedback.models import *
from django.contrib.contenttypes.models import ContentType

register = template.Library()

@register.simple_tag
def get_saved_post_count(user):
	x = len(SavedPost.objects.filter(profile=user.profile))
	return x

@register.simple_tag
def get_discussed_post_count(user):
	x = len(FollowedPost.objects.filter(profile=user.profile))
	return x

@register.simple_tag
def get_followers_count(user):
	followers = len(Follow.objects.filter(to_user=user.profile))
	return followers

@register.simple_tag
def get_following_count(user):
	following = len(Follow.objects.filter(from_user=user.profile))
	return following

@register.simple_tag
def get_photos_count(user):
	media=0
	queryset=Post.objects.filter(profile=user.profile)
	for post in queryset:
		if post.media and not post.is_video:
			media+=1
	return media

@register.simple_tag
def get_videos_count(user):
	media=0
	queryset=Post.objects.filter(profile=user.profile)
	for post in queryset:
		if post.media and post.is_video:
			media+=1
	return media

@register.simple_tag
def unread_notifs(user):
	n = Notification.objects.filter(profile=user.profile, active=True)
	return len(n)

@register.inclusion_tag('social/notifications.html')
def notifications(user):
	notifications=Notification.objects.filter(profile=user.profile)[:10]
	return {'notifications': notifications}

@register.filter('follows')
def follows(user1, user2):
	if Follow.objects.filter(from_user=user1.profile, to_user=user2.profile).exists():
		return True
	return False


@register.inclusion_tag('social/advertisements.html')
def advertisements():
	advertisements=list(Advertisement.objects.all())
	ads=random.sample(advertisements, 4)
	return {'advertisements': ads}


@register.filter('post_liked_by_user')
def post_liked_by_user(user, post):
	ct = ContentType.objects.get_for_model(post)
	if Like.objects.filter(profile=user.profile, content_type=ct, object_id=post.id).exists():
		return True
	return False

@register.filter('comment_liked_by_user')
def comment_liked_by_user(user, comment):
	ct = ContentType.objects.get_for_model(comment)
	if Like.objects.filter(profile=user.profile, content_type=ct, object_id=comment.id).exists():
		return True
	return False

@register.filter('has_saved')
def has_saved(user, post):
	ct = ContentType.objects.get_for_model(post)
	if SavedPost.objects.filter(profile=user.profile, content_type=ct, object_id=post.id).exists():
		return True
	return False

@register.filter('has_followed')
def has_followed(user, post):
	ct = ContentType.objects.get_for_model(post)
	if FollowedPost.objects.filter(profile=user.profile, content_type=ct, object_id=post.id).exists():
		return True
	return False


# def get_fees(doctor, clinic):
# 	try:
# 		fee=DoctorFee.objects.get(doctor=doctor, clinic=clinic).fees
# 		return fee
# 	except:
# 		return '-'

# register.filter('get_fees', get_fees)

# def get_clinic_schedule_start(doctor, clinic):
# 	try:
# 		today=datetime.today().date()
# 		week_day=calendar.day_name[today.weekday()]
# 		schedules = ClinicSchedule.objects.filter(clinic=clinic, doctor=doctor, day=week_day)
# 		if schedules.exists():
# 			sch=schedules.last()
# 		else:
# 			sch = ClinicSchedule.objects.filter(clinic=clinic, doctor=doctor).first()
# 		return sch.start
# 	except:
# 		return '-'

# def get_clinic_schedule_end(doctor, clinic):
# 	try:
# 		today=datetime.today().date()
# 		week_day=calendar.day_name[today.weekday()]
# 		schedules = ClinicSchedule.objects.filter(clinic=clinic, doctor=doctor, day=week_day)
# 		if schedules.exists():
# 			sch=schedules.last()
# 		else:
# 			sch = ClinicSchedule.objects.filter(clinic=clinic, doctor=doctor).first()
# 		return sch.end
# 	except:
# 		return '-'

# register.filter('get_clinic_schedule_start',get_clinic_schedule_start)

# register.filter('get_clinic_schedule_end',get_clinic_schedule_end)

# def get_lab_schedule_start(test):
# 	try:
# 		today=datetime.today().date()
# 		week_day=calendar.day_name[today.weekday()]
# 		schedules = LabSchedule.objects.filter(test=test, day=week_day)
# 		if schedules.exists():
# 			sch=schedules.last()
# 		else:
# 			sch = LabSchedule.objects.filter(test=test).first()
# 		return sch.start
# 	except:
# 		return '-'

# def get_lab_schedule_end(test):
# 	try:
# 		today=datetime.today().date()
# 		week_day=calendar.day_name[today.weekday()]
# 		schedules = LabSchedule.objects.filter(test=test, day=week_day)
# 		if schedules.exists():
# 			sch=schedules.last()
# 		else:
# 			sch = LabSchedule.objects.filter(test=test).first()
# 		return sch.end
# 	except:
# 		return '-'

# register.filter('get_lab_schedule_start',get_lab_schedule_start)

# register.filter('get_lab_schedule_end',get_lab_schedule_end)


# @register.simple_tag
# def pharmacy_order_length(pharmacy):
# 	return len(PharmacyOrder.objects.filter(pharmacy=pharmacy, reply_by_pharmacy__isnull=True))

# @register.simple_tag
# def pharmacy_confirmed_order_length(pharmacy):
# 	return len(PharmacyOrder.objects.filter(pharmacy=pharmacy, reply_by_pharmacy__confirmed=True, confirmed=False))

# @register.simple_tag
# def doctor_reports_length(doctor):
# 	return len(ClinicSlip.objects.filter(doctor=doctor, reply_by_doctor__isnull=False, reply_by_doctor__confirmed__isnull=True))

# @register.simple_tag
# def doctor_appointments_length(doctor):
# 	today=datetime.today()
# 	appointments=ClinicAppointment.objects.filter(doctor=doctor, date__gte=today, active=True)
# 	return len(appointments)

# @register.simple_tag
# def lab_appointments_length(lab):
# 	today=datetime.today()
# 	tests=lab.test_set.all()
# 	appointments=LabAppointment.objects.filter(test__in=tests, date__gte=today, active=True)
# 	return len(appointments)

# @register.simple_tag
# def lab_reports_length(lab):
# 	tests=lab.test_set.all()
# 	reports=LabAppointment.objects.filter(test__in=tests, active=False, report_generated=False)
# 	return len(reports)

# @register.simple_tag
# def type_of_user(user):
# 	try:
# 		u=user.patient
# 	except:
# 		try:
# 			u=user.doctor
# 		except:
# 			try:
# 				u=user.lab
# 			except:
# 				u=user.pharmacy
# 	return u

@register.simple_tag
def user_address(user):
	return user.profile.address.address

@register.simple_tag
def user_phone(user):
	return user.profile.phone.phone

# @register.simple_tag
# def doctor_rating(doctor):
# 	user=doctor.user
# 	ratings=Rating.objects.filter(user=user)
# 	sum=0
# 	for x in ratings:
# 		sum += x.value
	
# 	return u.phone.phone

