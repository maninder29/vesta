from .serializers import *
from customers import PyOpenGraph as InfoExtractor
from customers.api.serializers import ProfileSerializer
from customers.models import *
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.core.files import File
from django.db.models import Q
from friendship.models import *
from rest_framework import status
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from itertools import chain
from operator import attrgetter
from PIL import Image
from posts.models import *
from pyfcm import FCMNotification
import geocoder, pusher, validators

pusher_client = pusher.Pusher( app_id='303592', key='cf69569914b189660423', secret='963493a9c905d786e4d1', cluster='ap2', ssl=True )


class ChangeDpViewSet(ModelViewSet):
	parser_classes = [MultiPartParser]
	serializer_class = ProfileSerializer
	queryset = Profile.objects.all()
	def create(self, request):
		profile=request.user.profile
		dp=request.data.get('dp')
		profile.dp=dp
		image=Image.open(dp)
		path = settings.MEDIA_ROOT+'/'+'{0}/'.format(profile.user.email)
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
		profile.save()
		return Response()

class ChangeCoverViewSet(ModelViewSet):
	parser_classes = [MultiPartParser]
	serializer_class = ProfileSerializer
	queryset = User.objects.all()
	def create(self, request):
		profile=request.user.profile
		cover=request.data.get('cover')
		profile.cover=cover
		profile.save()
		return Response()

class ProfileViewSet(ModelViewSet):
	serializer_class=PostSerializer
	queryset = Post.objects.all()
	def retrieve(self, request, pk):
		profile=Profile.objects.get(id=pk)
		if profile.address:
			address = profile.address.address
			g=geocoder.google(address)
			city=g.city
			if not city:
				city = "Null"
		else:
			city = "Null"
		followers = Follow.objects.filter(to_user=profile)
		following = Follow.objects.filter(from_user=profile)
		dp, cover = profile.dp_url, profile.cover_url
		follow_status = "True" if Follow.objects.filter(from_user=request.user.profile, to_user=profile).exists() else "False"
		posts1 = Post.objects.filter(profile=profile)
		posts2 = WallPost.objects.filter(wall_profile=profile)
		if posts1 and posts2:
			posts = sorted( chain(posts1, posts2), key=attrgetter('timestamp'))
			posts.reverse()
		else:
			posts = posts1 if posts1 else posts2
		context={
			'name': profile.name,
			'city':city,
			'no_of_followers':str(len(followers)),
			'no_of_following':str(len(following)),
			'follow_status':follow_status,
			'dp':dp,
			'cover':cover,
			'posts':WallPostSerializer(posts, context={'request': request}, many=True).data,
		}
		return Response(context)

# follow/unfollow
class FollowViewSet(ModelViewSet):
	serializer_class=FollowerSerializer
	queryset = Follow.objects.all()
	def create(self, request):
		from_user = request.user.profile
		pk = int(request.data.get('id'))
		to_user = Profile.objects.get(id=pk)
		if not Follow.objects.filter(from_user=from_user, to_user=to_user).exists():
			instance = Follow(from_user=from_user, to_user=to_user)
			instance.save()
			title = from_user.name + ' followed you'
			link = reverse('profile', kwargs={'id':from_user.user.id})
			key=from_user.id
			n=Notification(profile=to_user, profile2=from_user, title=title, link=link, tag='f', key=key)
			n.save()
			pusher_client.trigger(to_user.user.username, 'notification', {
				'title': title,
				'id': n.id,
				'dp': from_user.dp_url,
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
		return Response()
	def destroy(self, request, pk):
		from_user = request.user.profile
		to_user = Profile.objects.get(id=pk)
		instance = Follow.objects.get(from_user=from_user, to_user=to_user)
		instance.delete()
		return Response()

# lists all followers of a particular user
class FollowersViewSet(ModelViewSet):
	serializer_class=FollowerSerializer
	queryset = Follow.objects.all()
	def retrieve(self, request, pk):
		profile=Profile.objects.get(id=pk)
		followers = Follow.objects.filter(to_user=profile)
		return Response(FollowerSerializer(followers, many=True).data)

# lists all following of a particular user
class FollowingViewSet(ModelViewSet):
	serializer_class=FollowingSerializer
	queryset = Follow.objects.all()
	def retrieve(self, request, pk):
		profile=Profile.objects.get(id=pk)
		following = Follow.objects.filter(from_user=profile)
		return Response(FollowingSerializer(following, many=True).data)

# lists all pictures of a particular user
class UserPhotosViewSet(ModelViewSet):
	serializer_class=ProfileSerializer
	queryset = Profile.objects.all()
	def retrieve(self, request, pk):
		profile=Profile.objects.get(id=pk)
		posts = Post.objects.filter(profile=profile)
		pics = []
		for post in posts:
			if post.media and not post.is_video:
				pics.append(post.media.url)
		return Response({'media':pics})

# lists all videos of a particular user
class UserVideosViewSet(ModelViewSet):
	serializer_class=ProfileSerializer
	queryset = Profile.objects.all()
	def retrieve(self, request, pk):
		profile=Profile.objects.get(id=pk)
		posts = Post.objects.filter(profile=profile)
		videos = []
		for post in posts:
			if post.media and post.is_video:
				videos.append(post.media.url)
		return Response({'media':videos})


def create_post(request, type_of_post):
	profile=request.user.profile
	content=request.data.get('content')
	media=request.data.get('media')
	post=Post( profile=profile, content=content, media=media, type_of_post=type_of_post )
	if not post.media: # og
		text = post.content
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
					# if og.site not in ["YouTube", "Vimeo"]:
					og.title=data.get('title')
					og.description=data.get('description')
					og.image=data.get('image')
					og.link=data.get('url')
					og.save()
					post.og=og
				except Exception as e:
					print str(e)
	post.save()
	return

def comment_liked_by_user(comment, profile):
	ct = ContentType.objects.get_for_model(comment)
	if Like.objects.filter(profile=profile, content_type=ct, object_id=comment.id).exists():
		return True
	return False

class NormalListViewSet(ModelViewSet):
	parser_classes = [MultiPartParser]
	serializer_class=PostSerializer
	queryset = Post.objects.all()
	def create(self, request, type_of_post):
		create_post(request, 'mySpace')
		return Response()

	def update(self, request, type_of_post, pk):
		if type_of_post == 'wall':
			post = WallPost.objects.get(id=pk)
		elif type_of_post == 'timeline':
			post = Post.objects.get(id=pk)
		if request.user != post.profile.user:
			return Response(status=status.HTTP_403_FORBIDDEN)
		if post.media:
			media_existed = True
			path = post.media.path
		else:
			media_existed = False
		if request.data.get('content'):
			post.content=request.data.get('content')
		if request.data.get('media'):
			post.media=request.data.get('media')
		post.save()
		if media_existed and post.media and post.media.path != path:
			os.remove(path)
		return Response()

	def list(self, request, type_of_post):
		queryset=Post.objects.filter(type_of_post='mySpace')
		return Response(PostSerializer(queryset, context={'request': request}, many=True).data)

	def retrieve(self, request, type_of_post, pk):
		if type_of_post == 'wall':
			post = WallPost.objects.get(id=pk)
		elif type_of_post == 'timeline':
			post = Post.objects.get(id=pk)
		ct=ContentType.objects.get_for_model(post)
		profile=request.user.profile
		post.views+=1
		post.save()
		comments=Comment.objects.filter(content_type=ct, object_id=post.id, parent=None)
		like_status=[]
		for c in comments:
			obj={"id": str(c.id)}
			obj["status"] = "True" if comment_liked_by_user(c, profile) else "False"
			like_status.append(obj)
		context={
			'post':PostSerializer(post, context={'request': request}).data,
			'comments':CommentSerializer(comments, many=True).data,
			'like_status':like_status
		}
		return Response(context)

	def destroy(self, request, type_of_post, pk):
		if type_of_post == 'wall':
			post = WallPost.objects.get(id=pk)
		elif type_of_post == 'timeline':
			post = Post.objects.get(id=pk)
		if request.user != post.profile.user:
			return Response(status=status.HTTP_403_FORBIDDEN)
		post.delete()
		return Response()

class DoctorListViewSet(ModelViewSet):
	parser_classes = [MultiPartParser]
	serializer_class=PostSerializer
	queryset = Post.objects.filter(type_of_post='differential')
	def create(self, request):
		user=request.user
		try:
			user.profile.doctor
		except:
			return Response(status=status.HTTP_403_FORBIDDEN)
		create_post(request, 'differential')
		return Response()

class PatientListViewSet(ModelViewSet):
	parser_classes = [MultiPartParser]
	serializer_class=PostSerializer
	queryset = Post.objects.filter(type_of_post='insights')
	def create(self, request):
		user=request.user
		try:
			user.profile.patient
		except:
			return Response(status=status.HTTP_403_FORBIDDEN)
		create_post(request, 'insights')
		return Response()

class LatestPostsInsightsViewSet(ModelViewSet):
	serializer_class=PostSerializer
	pagination_class=None
	queryset = Post.objects.filter(type_of_post='insights')
	def retrieve(self, request, pk):
		posts=Post.objects.filter(Q(id__gt=pk) & Q(type_of_post='insights'))
		return Response(PostSerializer(posts, context={'request': request}, many=True).data)

class LatestPostsDifferentialViewSet(ModelViewSet):
	serializer_class=PostSerializer
	pagination_class=None
	queryset = Post.objects.filter(type_of_post='differential')
	def retrieve(self, request, pk):
		posts=Post.objects.filter(Q(id__gt=pk) & Q(type_of_post='differential'))
		return Response(PostSerializer(posts, context={'request': request}, many=True).data)

class LatestPostsMyspaceViewSet(ModelViewSet):
	serializer_class=PostSerializer
	pagination_class=None
	queryset = Post.objects.filter(type_of_post='mySpace')
	def retrieve(self, request, pk):
		posts=Post.objects.filter(Q(id__gt=pk) & Q(type_of_post='mySpace'))
		return Response(PostSerializer(posts, context={'request': request}, many=True).data)

def post_liked_by_user(post, profile):
	ct = ContentType.objects.get_for_model(post)
	if Like.objects.filter(profile=profile, content_type=ct, object_id=post.id).exists():
		return True
	return False


class PostLikeViewSet(ModelViewSet):
	serializer_class=PostSerializer
	queryset = Post.objects.all()
	def retrieve(self, request, type_of_post, pk):
		if type_of_post == 'wall':
			post = WallPost.objects.get(id=pk)
		elif type_of_post == 'timeline':
			post = Post.objects.get(id=pk)
		ct=ContentType.objects.get_for_model(post)
		profile=request.user.profile
		if Like.objects.filter(profile=profile, content_type=ct, object_id=post.id).exists():
			l=Like.objects.get(profile=profile, content_type=ct, object_id=post.id)
			l.delete()
			post.like_count-=1
			post.save()
			return Response()
		Like(profile=profile, content_object=post).save()
		post.like_count+=1
		post.save()
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
		return Response()


class PostLikersViewSet(ModelViewSet):
	serializer_class=LikeSerializer
	queryset = Like.objects.all()
	def retrieve(self, request, type_of_post, pk):
		if type_of_post == 'wall':
			post = WallPost.objects.get(id=pk)
		elif type_of_post == 'timeline':
			post = Post.objects.get(id=pk)
		ct=ContentType.objects.get_for_model(post)
		likers=Like.objects.filter(content_type=ct, object_id=post.id)
		return Response(LikeSerializer(likers, many=True).data)

def user_commented_on_post(post, profile):
	ct = ContentType.objects.get_for_model(post)
	if Comment.objects.filter(content_type=ct, object_id=post.id, profile=profile).exists():
		return True
	return False


class CheckPostLikeCommentViewSet(ModelViewSet):
	serializer_class=PostSerializer
	queryset = Post.objects.all()
	def retrieve(self, request, type_of_post, pk):
		if type_of_post == 'wall':
			post = WallPost.objects.get(id=pk)
		elif type_of_post == 'timeline':
			post = Post.objects.get(id=pk)
		ct=ContentType.objects.get_for_model(post)
		profile=request.user.profile
		json = {}
		json['like'] = True if post_liked_by_user(post, profile) else False
		json['comment'] = True if user_commented_on_post(post, profile) else False
		json['saved'] = True if SavedPost.objects.filter(profile=profile, content_type=ct, object_id=post.id).exists() else False
		json['followed'] = True if FollowedPost.objects.filter(profile=profile, content_type=ct, object_id=post.id).exists() else False
		json['n_likes'] = str(post.like_count)
		json['n_comments'] = str(post.comment_count)
		json['n_views'] = str(post.views)
		return Response(json)


class CommentViewSet(ModelViewSet):
	serializer_class=CommentSerializer
	queryset = Comment.objects.all()
	def create(self, request, type_of_post):
		profile=request.user.profile
		pk=int(request.data.get('post'))
		if type_of_post == 'wall':
			post = WallPost.objects.get(id=pk)
		elif type_of_post == 'timeline':
			post = Post.objects.get(id=pk)
		ct = ContentType.objects.get_for_model(post)
		content=request.data.get('content')
		c=Comment(profile=profile, content_object=post, content=content, parent=None)
		c.save()
		post.comment_count+=1
		post.save()
		post_profile=post.profile
		if post_profile != profile:
			if post.content:
				title = profile.name + ' commented on your post "'+post.content[:60]+'"'
			else:
				title = profile.name + ' commented on your post'
			link = post.get_absolute_url() + "#" + str(c.id)
			key=post.id
			n=Notification(profile=post_profile, profile2=profile, title=title, link=link, tag='p', key=key)
			n.save()
			pusher_client.trigger(post_profile.username, 'notification', {
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
		return Response()

	def update(self, request, type_of_post, pk):
		comment=Comment.objects.get(id=pk)
		if request.user != comment.profile.user:
			return Response(status=status.HTTP_403_FORBIDDEN)
		content=request.data.get('content')
		comment.content=content
		comment.save()
		return Response()

	def destroy(self, instance, type_of_post, pk):
		comment=Comment.objects.get(id=pk)
		if request.user != comment.profile.user:
			return Response(status=status.HTTP_403_FORBIDDEN)
		comment.delete()


class CommentLikeViewSet(ModelViewSet):
	serializer_class=CommentSerializer
	queryset = Comment.objects.all()
	def retrieve(self, request, pk):
		comment=Comment.objects.get(id=pk)
		ct=ContentType.objects.get_for_model(comment)
		profile=request.user.profile
		if Like.objects.filter(profile=profile, content_type=ct, object_id=comment.id).exists():
			l=Like.objects.get(profile=profile, content_type=ct, object_id=comment.id)
			l.delete()
			comment.like_count-=1
			comment.save()
			return Response()
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
		return Response()


class CommentLikersViewSet(ModelViewSet):
	serializer_class=LikeSerializer
	queryset = Like.objects.all()
	def retrieve(self, request, pk):
		comment=Comment.objects.get(id=pk)
		ct=ContentType.objects.get_for_model(comment)
		likers=Like.objects.filter(content_type=ct, object_id=comment.id)
		return Response(LikeSerializer(likers, many=True).data)


class NotificationViewSet(ModelViewSet):
	serializer_class=NotificationSerializer
	queryset = Notification.objects.all()
	def list(self, request):
		profile = request.user.profile
		queryset = Notification.objects.filter(profile=profile)
		for n in queryset:
			if n.active:
				n.active=False
				n.save()
		return Response(NotificationSerializer(queryset, many=True).data)
	def update(self, request, pk):
		notif=Notification.objects.get(id=pk)
		if notif.active:
			notif.active=False
			notif.save()
		return Response()

class SavePostViewSet(ModelViewSet):
	serializer_class=PostSerializer
	queryset=Post.objects.all()
	def create(self, request, type_of_post):
		id=int(request.data.get('id'))
		if type_of_post == 'wall':
			post = WallPost.objects.get(id=id)
		elif type_of_post == 'timeline':
			post = Post.objects.get(id=id)
		ct = ContentType.objects.get_for_model(post)
		profile=request.user.profile
		if not SavedPost.objects.filter(profile=profile, content_type=ct, object_id=post.id).exists():
			instance=SavedPost(profile=profile, content_object=post)
			instance.save()
			return Response()
		else:
			instance=SavedPost.objects.get(profile=profile, content_type=ct, object_id=post.id)
			instance.delete()
			return Response()

	def list(self, request, type_of_post):
		profile=request.user.profile
		posts=[i.content_object for i in SavedPost.objects.filter(profile=profile)]
		return Response(WallPostSerializer(posts, context={'request': request}, many=True).data)


class DiscussPostViewSet(ModelViewSet):
	serializer_class=PostSerializer
	queryset=Post.objects.all()
	def create(self, request, type_of_post):
		id=int(request.data.get('id'))
		if type_of_post == 'wall':
			post = WallPost.objects.get(id=id)
		elif type_of_post == 'timeline':
			post = Post.objects.get(id=id)
		ct = ContentType.objects.get_for_model(post)
		profile=request.user.profile
		if not FollowedPost.objects.filter(profile=profile, content_type=ct, object_id=post.id).exists():
			instance=FollowedPost(profile=profile, content_object=post)
			instance.save()
			return Response()
		else:
			instance=FollowedPost.objects.get(profile=profile, content_type=ct, object_id=post.id)
			instance.delete()
			return Response()

	def list(self, request, type_of_post):
		profile=request.user.profile
		posts=[i.content_object for i in FollowedPost.objects.filter(profile=profile)]
		return Response(WallPostSerializer(posts, context={'request': request}, many=True).data)

class DrawerViewSet(ModelViewSet):
	serializer_class=ProfileSerializer
	queryset=Profile.objects.all()
	def list(self, request):
		profile=request.user.profile
		notifications = Notification.objects.filter(profile=profile)[:10]
		photos=videos=0
		queryset=Post.objects.filter(profile=profile)
		for post in queryset:
			if post.media:
				if post.is_video:
					videos+=1
				else:
					photos+=1
		context={
			'saved':SavedPost.objects.filter(profile=profile).count(),
			'discussed':FollowedPost.objects.filter(profile=profile).count(),
			'followers':Follow.objects.filter(to_user=profile).count(),
			'following':Follow.objects.filter(from_user=profile).count(),
			'photos':photos,
			'videos':videos,
			'unread_notif_count':Notification.objects.filter(profile=profile, active=True).count(),
			'notifications':NotificationSerializer(notifications, many=True).data
		}
		return Response(context)