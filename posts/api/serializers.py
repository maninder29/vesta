from rest_framework.serializers import ModelSerializer, SerializerMethodField, CurrentUserDefault
from posts.models import *
from friendship.models import *
from customers.api.serializers import ProfileSerializer


class OpenGraphSerializer(ModelSerializer):
	class Meta:
		model=OpenGraph
		fields=['title', 'description', 'image', 'link']

class PostSerializer(ModelSerializer):
	saved=SerializerMethodField()
	def get_saved(self, instance):
		ct=ContentType.objects.get_for_model(instance)
		profile=self.context.get('request').user.profile
		return True if SavedPost.objects.filter(profile=profile, content_type=ct, object_id=instance.id).exists() else False

	discussed=SerializerMethodField()
	def get_discussed(self, instance):
		ct=ContentType.objects.get_for_model(instance)
		profile=self.context.get('request').user.profile
		return True if FollowedPost.objects.filter(profile=profile, content_type=ct, object_id=instance.id).exists() else False

	type=SerializerMethodField()
	def get_type(self, instance):
		return instance.type

	user=SerializerMethodField()
	def get_user(self, instance):
		return ProfileSerializer(instance.profile).data

	og=OpenGraphSerializer()
	class Meta:
		model=Post
		fields=['id', 'user', 'content', 'timestamp', 'media', 'like_count', 'comment_count', 'views', 'og', 'type', 'saved', 'discussed']

class WallPostSerializer(ModelSerializer):
	saved=SerializerMethodField()
	def get_saved(self, instance):
		ct=ContentType.objects.get_for_model(instance)
		profile=self.context.get('request').user.profile
		return True if SavedPost.objects.filter(profile=profile, content_type=ct, object_id=instance.id).exists() else False

	discussed=SerializerMethodField()
	def get_discussed(self, instance):
		ct=ContentType.objects.get_for_model(instance)
		profile=self.context.get('request').user.profile
		return True if FollowedPost.objects.filter(profile=profile, content_type=ct, object_id=instance.id).exists() else False

	type=SerializerMethodField()
	def get_type(self, instance):
		return instance.type

	user=SerializerMethodField()
	def get_user(self, instance):
		return ProfileSerializer(instance.profile).data

	wall_profile=SerializerMethodField()
	def get_wall_profile(self, instance):
		try:
			return ProfileSerializer(instance.wall_profile).data
		except:
			pass

	og=OpenGraphSerializer()
	class Meta:
		model=WallPost
		fields=['id', 'user', 'wall_profile', 'content', 'timestamp', 'media', 'like_count', 'comment_count', 'views', 'og', 'type', 'saved', 'discussed']

class LikeSerializer(ModelSerializer):
	user=SerializerMethodField()
	def get_user(self, instance):
		return ProfileSerializer(instance.profile).data
	class Meta:
		model=Like
		fields=['user']

class CommentSerializer(ModelSerializer):
	user=SerializerMethodField()
	def get_user(self, instance):
		return ProfileSerializer(instance.profile).data
	class Meta:
		model=Comment
		fields=['id','user','content','timestamp', 'like_count']

class FollowerSerializer(ModelSerializer):
	from_user=ProfileSerializer()
	class Meta:
		model=Follow
		fields=['from_user']

class FollowingSerializer(ModelSerializer):
	to_user=ProfileSerializer()
	class Meta:
		model=Follow
		fields=['to_user']

class NotificationSerializer(ModelSerializer):
	dp=SerializerMethodField()
	def get_dp(self, instance):
		return instance.profile2.thumbnail_url
	class Meta:
		model=Notification
		fields=['id','title','tag','key','dp','active']