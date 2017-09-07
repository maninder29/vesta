from .models import *
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render,redirect,reverse
from posts.models import Notification
from pyfcm import FCMNotification
import pusher

pusher_client=pusher.Pusher(app_id='303592',key='cf69569914b189660423',secret='963493a9c905d786e4d1',cluster='ap2',ssl=True)

@login_required
def follow(request, id):
	from_user = request.user.profile
	to_user = User.objects.get(id=id).profile
	if not Follow.objects.filter(from_user=from_user, to_user=to_user).exists():
		instance = Follow(from_user=from_user, to_user=to_user)
		instance.save()
		title = str(from_user.name) + ' followed you'
		link = reverse('profile', kwargs={'id':from_user.user.id})
		key=from_user.user.id
		n=Notification(profile=to_user, profile2=from_user, title=title, link=link, tag='f', key=key)
		n.save()
		pusher_client.trigger(to_user.user.username, 'notification', {
			'title': title,
			'id': n.id,
			'dp': from_user.thumbnail_url,
			})
		# try:
		# 	push_service = FCMNotification(api_key=settings.FCM_API_KEY_SOCIAL)
		# 	devices = FCMDevice.objects.filter(user=comment_user)
		# 	registration_ids=[d.registration_id for d in devices]
		# 	data={
		# 		# "title" : title,
		# 		# "id":pk,
		# 	}
		# 	result = push_service.notify_multiple_devices(registration_ids=registration_ids, message_title='Vesta', message_body=title, data_message=data, sound="Default", message_icon='vestapp.in/static/vesta-social-logo.png')
		# except Exception as e:
		# 	# print (str(e))
		# 	pass
	return redirect(request.META['HTTP_REFERER'])

@login_required
def unfollow(request, id):
	from_user = request.user.profile
	to_user = User.objects.get(id=id).profile
	instance = Follow.objects.get(from_user=from_user, to_user=to_user)
	instance.delete()
	return redirect(request.META['HTTP_REFERER'])

@login_required
def remove_follower(request, id):
	from_user = User.objects.get(id=id).profile
	to_user = request.user.profile
	instance = Follow.objects.get(from_user=from_user, to_user=to_user)
	instance.delete()
	return redirect(request.META['HTTP_REFERER'])


@login_required
def all_followers(request, id):
	profile=User.objects.get(id=id).profile
	followers = [f.from_user for f in Follow.objects.filter(to_user=profile)]
	return render(request, "social/search_user.html", {"users": followers, "category": "Followers"})

@login_required
def all_following(request, id):
	profile=User.objects.get(id=id).profile
	following = [f.to_user for f in Follow.objects.filter(from_user=profile)]
	return render(request, "social/search_user.html", {"users": following, "category": "Following"})