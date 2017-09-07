from .forms import *
from .models import *
from customers import PyOpenGraph as InfoExtractor
from customers.models import Profile
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.core.files import File
from django.db.models import Q
from django.http import JsonResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.utils.timesince import timesince
from friendship.models import *
from itertools import chain
from operator import attrgetter
from PIL import Image
from pyfcm import FCMNotification
import os, pusher, validators

pusher_client = pusher.Pusher(app_id='303592',key='cf69569914b189660423',secret='963493a9c905d786e4d1',cluster='ap2',ssl=True)

init_page_size = 20

post_size = 5

def post_form(request):
	form = PostForm(request.POST or None, request.FILES or None)
	if form.is_valid():
		profile=request.user.profile
		instance = form.save(commit=False)
		instance.profile = profile
		instance.type_of_post = request.POST.get('type')
		thumbnail = request.POST.get('thumbnail')
		if thumbnail:
			thumbnail=thumbnail.split(',')[1]
			path = settings.MEDIA_ROOT+'/'+'{0}/'.format(profile.user.email)
			if not os.path.exists(path):
				os.makedirs(path)
			path+="imageToSave.jpeg"
			with open(path, "wb") as fh:
				fh.write(thumbnail.decode('base64'))
			local_file=open(path, 'rb')
			instance.poster.save('dpthumb.jpg', File(local_file), save=True)
			local_file.close()
			os.remove(path)
		if not instance.media:
			text = instance.content
			text = text.split('http')
			if len(text) != 1:
				text = text[1]
				text = text.split(" ")
				url = "http" + str(text[0])
				if validators.url(url):
					try:
						data = InfoExtractor.PyOpenGraph(url).metadata
						og=OpenGraph()
						og.site=data.get('site_name')
						og.title=data.get('title')
						og.description=data.get('description')
						og.image=data.get('image')
						og.link=data.get('url')
						og.save()
						instance.og=og
					except Exception as e:
						pass
		instance.save()
		return redirect(instance)
	return form


def calc_id_from_queryset_length(filter):
	queryset=Post.objects.filter(type_of_post=filter)[:init_page_size]
	length = len(queryset)
	if(length == init_page_size):
		id=str(queryset[init_page_size-1].id)
	elif length == 0:
		id = 0
	else:
		id=str(queryset[length-1].id)
	return id, queryset


@login_required
def list_normal(request):
	form = post_form(request)
	if str(type(form)) != "<class 'posts.forms.PostForm'>":
		return form
	id, queryset = calc_id_from_queryset_length('mySpace')
	context = {
		"object_list": queryset,
		'form':form,
		'category' : 'mySpace',
		'id':id,
	}
	return render(request, "common/base.html", context)

@login_required
def list_doctor(request):
	form = post_form(request)
	if str(type(form)) != "<class 'posts.forms.PostForm'>":
		return form
	id, queryset = calc_id_from_queryset_length('differential')
	context = {
		"object_list": queryset,
		'form':form,
		'category' : 'differential',
		'id': id,
	}
	return render(request, "common/base.html", context)

@login_required
def list_patient(request):
	form = post_form(request)
	if str(type(form)) != "<class 'posts.forms.PostForm'>":
		return form
	id, queryset = calc_id_from_queryset_length('insights')
	context = {
		"object_list": queryset,
		'form':form,
		'category' : 'insights',
		'id': id,
	}
	return render(request, "common/base.html", context)

def post_data(posts, user):
	length = len(posts)
	if(length == post_size):
		id=str(posts[post_size-1].id)
	else:
		id=str(posts[length-1].id)
	data=[]
	for p in posts:
		profile=p.profile
		dictt={
			'id': str(p.id),
			'name': profile.name,
			'dp': profile.thumbnail_url,
			'user_id': str(profile.user.id),
			# 'timestamp': timesince(p.timestamp),
			'content': p.content[:360],
			'likes': str(p.like_count),
			'comments': str(p.comment_count),
			'views' : str(p.views),
			'unique_id':str(id),
		}
		# if p.type == 'wall':
		# 	dictt['wall_post'] = 1
		# 	dictt['wall_post_user_name'] = p.wall_profile.profile.name
		# 	dictt['wall_post_user_id'] = p.wall_profile.id
		# 	dictt['wall_post_user_vip'] = 1 if p.wall_profile.profile.vip else 0
		# else:
		# 	dictt['wall_post'] = 0
		dictt['long_post'] = 1 if len(p.content)>360 else 0
		dictt['user_status'] = 1 if profile == user else 0
		dictt['vip'] = 1 if profile.vip else 0
		ct=ContentType.objects.get_for_model(p)
		dictt['like_status'] = 1 if Like.objects.filter(profile=profile, content_type=ct, object_id=p.id).exists() else 0
		if p.media:
			dictt['flag'] = 2 if p.is_video else 1
			dictt['media'] = p.media.url
		elif p.og:
			if p.og.site in ["YouTube", "Vimeo"]:
				dictt['flag'] = 3
				dictt['embed'] = p.og.embed_src
			else:
				dictt['flag'] = 4
				dictt['og_title'] = p.og.title
				dictt['og_description'] = p.og.description
				dictt['og_image'] = p.og.image
				dictt['og_link'] = p.og.link
		else:
			dictt['flag'] = 5

		if p.content:
			dictt['text']=p.content[:120]
		else:
			dictt['text']='Vesta - Your digital healthcare ecosystem'
		data.append(dictt)
	return data

@login_required
def new_myspace_list(request, id):
	if request.is_ajax():
		try:
			posts=Post.objects.filter(id__lt=id, type_of_post='mySpace')[:post_size]
			data=post_data(posts, request.user.profile)
			return JsonResponse({ 'posts': data })
		except Exception as e:
			return JsonResponse({ 'status': 'deactive' })
	else:
		return redirect('list_normal')

@login_required
def new_differential_list(request, id):
	if request.is_ajax():
		try:
			posts=Post.objects.filter(id__lt=id, type_of_post='differential')[:post_size]
			data=post_data(posts, request.user.profile)
			return JsonResponse({ 'posts': data })
		except:
			return JsonResponse({ 'status': 'deactive' })
	else:
		return redirect('list_doctor')

@login_required
def new_insights_list(request, id):
	if request.is_ajax():
		try:
			posts=Post.objects.filter(id__lt=id, type_of_post='insights')[:post_size]
			data=post_data(posts, request.user.profile)
			return JsonResponse({ 'posts': data })
		except:
			return JsonResponse({ 'status': 'deactive' })
	else:
		return redirect('list_patient')

def post_detail(request, type_of_post, id=None):
	if type_of_post == 'wall':
		instance = get_object_or_404(WallPost, id=id)
	elif type_of_post == 'timeline':
		instance = get_object_or_404(Post, id=id)
	ct = ContentType.objects.get_for_model(instance)
	comments=Comment.objects.filter(content_type=ct, object_id=instance.id, parent=None)
	form=CommentForm(request.POST or None)
	if form.is_valid():
		user=request.user
		if not user.is_authenticated():
			return redirect('home')
		content=form.cleaned_data.get("content")
		try:
			parent_id=int(request.POST.get("parent_id"))
			parent=get_object_or_404(Comment,id=parent_id)
		except:
			parent=None
		profile=user.profile
		c=Comment(profile=profile,content_object=instance,content=content,parent=parent)
		c.save()
		post_profile=instance.profile
		if profile != post_profile:
			if instance.content:
				title = profile.name + ' commented on your post "'+instance.content[:60]+'"'
			else:
				title = profile.name + ' commented on your post'
			link = instance.get_absolute_url() + "#" + str(c.id)
			key=instance.id
			n=Notification(profile=post_profile, profile2=profile, title=title, link=link, tag='p', key=key)
			n.save()
			pusher_client.trigger(post_profile.user.username, 'notification', {
				'title': title,
				'id': n.id,
				'dp': profile.thumbnail_url,
				})
			# try:
			# 	push_service = FCMNotification(api_key=settings.FCM_API_KEY_SOCIAL)
			# 	devices = FCMDevice.objects.filter(user=post_user)
			# 	registration_ids=[d.registration_id for d in devices]
			# 	data={}
			# 	result = push_service.notify_multiple_devices(registration_ids=registration_ids, message_title='Vesta', message_body=title, data_message=data, sound="Default", message_icon='vestapp.in/static/vesta-social-logo.png')
			# except Exception as e:
			# 	pass
		instance.comment_count+=1
		instance.views-=1
		instance.save()
		return redirect(instance)
	instance.views+=1
	instance.save()
	context = {
		"post": instance,
		"comments":comments,
		"form":form,
		"single_post":True,
	}
	return render(request, "social/comment.html", context)

@login_required
def post_update(request, type_of_post, id=None):
	if type_of_post == 'wall':
		instance = get_object_or_404(WallPost, id=id)
		if request.user != instance.profile.user:
			raise Http404
		if instance.media:
			media_existed = True
			path = instance.media.path
		else:
			media_existed = False

		form = WallPostForm(request.POST or None, request.FILES or None, instance=instance)
		if form.is_valid():
			instance = form.save()
			if request.POST.get('media-clear') == 'on' or (media_existed and instance.media and instance.media.path != path):
				os.remove(path)
			return redirect(instance)
	elif type_of_post == 'timeline':
		instance = get_object_or_404(Post, id=id)
		if request.user != instance.profile.user:
			raise Http404
		if instance.media:
			media_existed = True
			path = instance.media.path
		else:
			media_existed = False

		form = PostForm(request.POST or None, request.FILES or None, instance=instance)
		if form.is_valid():
			instance = form.save()
			if request.POST.get('media-clear') == 'on' or (media_existed and instance.media and instance.media.path != path):
				os.remove(path)
			return redirect(instance)

	context = {
		"instance": instance,
		"form":form,
		"value":"edit",
	}
	return render(request, "social/editPost.html", context)

@login_required
def post_delete(request, type_of_post, id=None):
	if type_of_post == 'wall':
		post = get_object_or_404(WallPost, id=id)
	elif type_of_post == 'timeline':
		post = get_object_or_404(Post, id=id)
	if request.user != post.profile.user:
		raise Http404
	post.delete()
	url = request.META['HTTP_REFERER']
	for i in ['myspace', 'differential', 'insights', 'profile', 'saved', 'discussion']:
		if i in url:
			return redirect(url)
	return redirect('list_normal')

@login_required
def post_like(request, type_of_post, id):
	if request.is_ajax():
		if type_of_post == 'wall':
			post = get_object_or_404(WallPost, id=id)
		elif type_of_post == 'timeline':
			post = get_object_or_404(Post, id=id)
		ct=ContentType.objects.get_for_model(post)
		profile=request.user.profile
		if Like.objects.filter(profile=profile, content_type=ct, object_id=post.id).exists():
			l=get_object_or_404(Like, profile=profile, content_type=ct, object_id=post.id)
			l.delete()
			post.like_count-=1
			post.save()
			return JsonResponse({})
		Like(profile=profile, content_object=post).save()
		post_profile=post.profile
		if profile != post_profile:
			if post.content:
				title = profile.name + ' liked your post "'+post.content[:60]+'"'
			else:
				title = profile.name + ' liked your post'
			link = post.get_absolute_url()
			key=post.id
			n=Notification(profile=post_profile, profile2=profile, title=title, link=link, tag='p', key=key)
			n.save()
			pusher_client.trigger(post_profile.user.username, 'notification', {
				'title': title,
				'id': n.id,
				'dp': profile.thumbnail_url,
				})
			# try:
			# 	push_service = FCMNotification(api_key=settings.FCM_API_KEY_SOCIAL)
			# 	devices = FCMDevice.objects.filter(user=post_user)
			# 	registration_ids=[d.registration_id for d in devices]
			# 	data={
			# 		# "title" : title,
			# 		# "id":pk,
			# 	}
			# 	result = push_service.notify_multiple_devices(registration_ids=registration_ids, message_title='Vesta', message_body=title, data_message=data, sound="Default", message_icon='vestapp.in/static/vesta-social-logo.png')
			# except Exception as e:
			# 	# print (str(e))
			# 	pass
		post.like_count+=1
		post.save()
		return JsonResponse({})
	else:
		return redirect("list_normal")

@login_required
def get_post_likers(request, type_of_post, id):
	if request.is_ajax():
		if type_of_post == 'wall':
			post = get_object_or_404(WallPost, id=id)
		elif type_of_post == 'timeline':
			post = get_object_or_404(Post, id=id)
		ct=ContentType.objects.get_for_model(post)
		likers=[l.profile for l in Like.objects.filter(content_type=ct, object_id=post.id)]
		data=[]
		for liker in likers:
			obj={
				'name': liker.name,
				'id': liker.user.id,
				'dp': liker.thumbnail_url,
			}
			data.append(obj)
		return JsonResponse({'data':data})

@login_required
def comment_delete(request, id):
	comment=get_object_or_404(Comment, id=id)
	if request.user != comment.profile.user:
		raise Http404
	comment.delete()
	return redirect(request.META['HTTP_REFERER'])

@login_required
def comment_update(request, id):
	if request.is_ajax() and request.POST:
		comment=get_object_or_404(Comment, id=id)
		if request.user != comment.profile.user:
			raise Http404
		comment.content=request.POST.get('content')
		comment.save()
		return JsonResponse({})

@login_required
def comment_like(request, id):
	if request.is_ajax():
		comment=get_object_or_404(Comment, id=id)
		ct=ContentType.objects.get_for_model(comment)
		profile=request.user.profile
		if Like.objects.filter(profile=profile, content_type=ct, object_id=comment.id).exists():
			l=get_object_or_404(Like, profile=profile, content_type=ct, object_id=comment.id)
			l.delete()
			comment.like_count-=1
			comment.save()
			return JsonResponse({})
		Like(profile=profile, content_object=comment).save()
		comment_profile=comment.profile
		if profile != comment_profile:
			title = profile.name + ' liked your comment "'+comment.content[:60]+'"'
			link = comment.content_object.get_absolute_url() + "#" + str(comment.id)
			key=comment.content_object.id
			n=Notification(profile=comment_profile, profile2=profile, title=title, link=link, tag='p', key=key)
			n.save()
			pusher_client.trigger(comment_profile.user.username, 'notification', {
				'title': title,
				'id': n.id,
				'dp': profile.thumbnail_url,
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
		comment.like_count+=1
		comment.save()
		return JsonResponse({})
	else:
		return redirect("list_normal")


@login_required
def profile(request, id):
	user=User.objects.get(id=id)
	profile=user.profile

	followers = [f.from_user for f in Follow.objects.filter(to_user=profile)]
	following = [f.to_user for f in Follow.objects.filter(from_user=profile)]

	posts1 = Post.objects.filter(profile=profile)
	posts2 = WallPost.objects.filter(wall_profile=profile)
	if posts1 and posts2:
		posts = sorted( chain(posts1, posts2), key=attrgetter('timestamp'))
		posts.reverse()
	else:
		posts = posts1 if posts1 else posts2
	# queryset=posts[:init_page_size]
	# length = len(queryset)
	# if(length == init_page_size):
	# 	id=str(queryset[init_page_size-1].id)
	# elif length == 0:
	# 	id = 0
	# else:
	# 	id=str(queryset[length-1].id)

	dp_form = ProfilePicForm(request.POST or None, request.FILES or None)
	if dp_form.is_valid():
		dp=dp_form.cleaned_data.get('dp')
		profile.dp=dp
		image=Image.open(dp)
		path = settings.MEDIA_ROOT+'/'+'{0}/'.format(user.email)
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
		try:
			resized_image.save(path)
		except:
			pass
		local_file=open(path, 'rb')
		profile.thumbnail.save('dpthumb.jpg', File(local_file), save=True)
		local_file.close()
		os.remove(path)
		return redirect(reverse('profile', kwargs={"id":user.id}))

	cover_form = CoverPicForm(request.POST or None, request.FILES or None)
	if cover_form.is_valid():
		profile.cover=cover_form.cleaned_data.get('cover')
		profile.save()
		return redirect(reverse('profile', kwargs={"id":user.id}))

	form = WallPostForm(request.POST or None, request.FILES or None)
	if form.is_valid():
		request_user=request.user.profile
		instance = form.save(commit=False)
		instance.profile = request_user
		instance.wall_profile = profile
		thumbnail = request.POST.get('thumbnail')
		if thumbnail:
			thumbnail=thumbnail.split(',')[1]
			path = settings.MEDIA_ROOT+'/'+'{0}/'.format(profile.user.email)
			if not os.path.exists(path):
				os.makedirs(path)
			path+="imageToSave.jpeg"
			with open(path, "wb") as fh:
				fh.write(thumbnail.decode('base64'))
			local_file=open(path, 'rb')
			instance.poster.save('dpthumb.jpg', File(local_file), save=True)
			local_file.close()
			os.remove(path)
		if not instance.media:
			text = instance.content
			text = text.split('http')
			if len(text) != 1:
				text = text[1]
				text = text.split(" ")
				url = "http" + str(text[0])
				if validators.url(url):
					try:
						data = InfoExtractor.PyOpenGraph(url).metadata
						og=OpenGraph()
						og.site=data.get('site_name')
						og.title=data.get('title')
						og.description=data.get('description')
						og.image=data.get('image')
						og.link=data.get('url')
						og.save()
						instance.og=og
					except Exception as e:
						pass
		instance.save()
		return redirect(reverse('profile', kwargs={"id":user.id}))
	
	pics = []
	videos = []
	for post in posts:
		if post.media:
			url = post.media.url
			videos.append(url) if post.is_video else pics.append(url)
				
	context = {
		'followers':followers[:4],
		'following':following[:4],
		'object_list':posts,
		'profile_user':user,
		'pics':pics[:4],
		'videos':videos[:4],
		# 'id':id,
		'category':'profile'
	}
	return render(request, 'social/profile.html', context)


# @login_required
# def new_profile_list(request, id, user_id):
# 	if request.is_ajax():
# 		try:
# 			user=User.objects.get(id=user_id)
# 			username = user.username
# 			posts=Post.objects.filter(Q(id__lt=id) & ( (Q(user=user) & Q(type_of_post__in=types)) | Q(type_of_post=username) ))[:post_size]
# 			data=post_data(posts, request.user)
# 			return JsonResponse({ 'posts': data })
# 		except Exception as e:
# 			return JsonResponse({ 'status': 'deactive' })
# 	else:
# 		return redirect('list_normal')


def deactivate_notification(request, id):
	notif=get_object_or_404(Notification, id=id)
	if notif.active:
		notif.active=False
		notif.save()
	return redirect(notif.link)

def all_notifications(request):
	profile = request.user.profile
	notifications = Notification.objects.filter(profile=profile)
	for n in notifications:
		if n.active:
			n.active=False
			n.save()
	return render(request, "social/all_notifications.html", {"notifications":notifications})

def mark_all_notifications_read(request):
	profile = request.user.profile
	notifications = Notification.objects.filter(profile=profile)
	for n in notifications:
		if n.active:
			n.active=False
			n.save()
	return redirect(request.META['HTTP_REFERER'])

@login_required
def all_photos(request, id):
	profile=User.objects.get(id=id).profile
	media=[]
	queryset=Post.objects.filter(profile=profile)
	for post in queryset:
		if post.media and not post.is_video:
			media.append(post.media.url)
	return render(request, "social/all_photos.html", {'media':media})

@login_required
def all_videos(request, id):
	profile=User.objects.get(id=id).profile
	media=[]
	queryset=Post.objects.filter(profile=profile)
	for post in queryset:
		if post.media and post.is_video:
			media.append(post.media.url)
	return render(request, "social/all_videos.html", {'media':media})


@login_required
def all_users(request):
	if request.is_ajax():
		users=Profile.objects.all()
		data = {}
		for u in users:
			data[u.name]=None
		return JsonResponse(data)
	return redirect('profile', kwargs={'id':id})


@login_required
def search_user(request):
	name = request.GET.get('q')
	name_list = name.split(' ')
	if len(name_list) > 1:
		users = Profile.objects.filter(Q(name__icontains=name_list[0]) & Q(name__icontains=name_list[-1]))
	else:
		users = Profile.objects.filter(Q(name__icontains=name) | Q(name__icontains=name))
	message=None
	if not users.exists():
		users = Profile.objects.all()
		message = "Sorry, we can't find anything related to the query. Other community members are:-"
	return render(request, "social/search_user.html", {'users':users.order_by('name'), 'category':'Search user', 'message':message})


@login_required
def save_post(request, type_of_post, id):
	if request.is_ajax() and request.POST:
		if type_of_post == 'wall':
			post = get_object_or_404(WallPost, id=id)
		elif type_of_post == 'timeline':
			post = get_object_or_404(Post, id=id)
		ct = ContentType.objects.get_for_model(post)
		profile=request.user.profile
		if not SavedPost.objects.filter(profile=profile, content_type=ct, object_id=post.id).exists():
			instance=SavedPost(profile=profile, content_object=post)
			instance.save()
			message = "Saved"
			text = '<i class="fa fa-download" aria-hidden="true"></i>Unsave'
		else:
			instance=SavedPost.objects.get(profile=profile, content_type=ct, object_id=post.id)
			instance.delete()
			message = "Unsaved"
			text = '<i class="fa fa-download" aria-hidden="true"></i>Save'
		return JsonResponse({'message': message, 'text':text})

@login_required
def follow_post(request, type_of_post, id):
	if request.is_ajax() and request.POST:
		if type_of_post == 'wall':
			post = get_object_or_404(WallPost, id=id)
		elif type_of_post == 'timeline':
			post = get_object_or_404(Post, id=id)
		ct = ContentType.objects.get_for_model(post)
		profile=request.user.profile
		if not FollowedPost.objects.filter(profile=profile, content_type=ct, object_id=post.id).exists():
			instance=FollowedPost(profile=profile, content_object=post)
			instance.save()
			message = "Added to discussion"
			text = '<i class="fa fa-envelope" aria-hidden="true"></i>Remove'
		else:
			instance=FollowedPost.objects.get(profile=profile, content_type=ct, object_id=post.id)
			instance.delete()
			message = "Removed from discussion"
			text = '<i class="fa fa-envelope" aria-hidden="true"></i>Discuss'
		return JsonResponse({'message': message, 'text':text})

@login_required
def followed_posts(request):
	profile=request.user.profile
	posts=[i.content_object for i in FollowedPost.objects.filter(profile=profile)]
	return render(request, 'social/post_list.html', {'posts': posts, 'category': 'Discussion'})

@login_required
def saved_posts(request):
	profile=request.user.profile
	posts=[i.content_object for i in SavedPost.objects.filter(profile=profile)]
	return render(request, 'social/post_list.html', {'posts': posts, 'category': 'Saved posts'})