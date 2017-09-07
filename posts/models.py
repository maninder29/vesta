from customers.models import Profile
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.db.models.signals import pre_delete
from django.db import models
import os
import datetime


class OpenGraph(models.Model):
    title = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    image = models.TextField(null=True, blank=True)
    link = models.TextField(null=True, blank=True)
    site = models.TextField(null=True, blank=True)
    def __unicode__(self):
        return self.title

    @property
    def embed_src(self):
        url = self.link;
        if self.site == "YouTube":
            id = url.split("?v=")[1];
            src = "https://www.youtube.com/embed/" + id;
        else:
            id = url.split("m/")[1];
            src = "https://player.vimeo.com/video/" + id;
        return src

def media_upload(instance, filename):
    timestamp = datetime.datetime.now().strftime("%d_%m_%Y__%H_%M")
    ext = filename.split('.')[-1]
    filename = timestamp+'.'+ext
    return '{0}/posts/{1}'.format(instance.profile.user.email, filename)

def poster_upload(instance, filename):
    timestamp = datetime.datetime.now().strftime("%d_%m_%Y__%H_%M")
    ext = filename.split('.')[-1]
    filename = timestamp+'_poster.'+ext
    return '{0}/posts/{1}'.format(instance.profile.user.email, filename)


class Post(models.Model):
    TYPE_CHOICES=(
        ('mySpace', 'mySpace'),
        ('differential', 'differential'),
        ('insights', 'insights')
        )
    profile = models.ForeignKey(Profile)
    content = models.TextField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now=False, auto_now_add=True)
    # updated = models.DateTimeField(auto_now=True, auto_now_add=False)
    media = models.FileField(upload_to=media_upload, null=True, blank=True)
    poster = models.ImageField(upload_to=poster_upload, null=True, blank=True)
    like_count = models.PositiveIntegerField(default=0)
    comment_count = models.PositiveIntegerField(default=0)
    views = models.PositiveIntegerField(default=0)
    type_of_post = models.CharField(max_length=45, choices=TYPE_CHOICES, null=True, blank=True)
    og = models.OneToOneField(OpenGraph, null=True, blank=True)
    comments = GenericRelation('Comment')
    class Meta:
        ordering=["-timestamp"]

    def __unicode__(self):
        return str(self.profile)+str(self.id)

    @property
    def type(self):
        return 'timeline'

    def get_absolute_url(self):
        return reverse("detail", kwargs={"id": self.id, "type_of_post": "timeline"})

    @property
    def is_video(self):
        name=self.media.name
        extention = name.split('.')[-1]
        if extention in ['mp4','MP4','3gp','3GP','obb','OBB']:
            return True
        return False


def post_pre_delete_reciever(sender, instance, *args, **kwargs):
    try:
        if instance.og:
            instance.og.delete()
        if instance.media:
            path=instance.media.path
            os.remove(path)
        if instance.poster:
            path=instance.poster.path
            os.remove(path)
        ct = ContentType.objects.get_for_model(instance)
        pk = instance.id
        comments = Comment.objects.filter(content_type=ct, object_id=pk)
        if comments.exists():
            comments.delete()
        likes=Like.objects.filter(content_type=ct, object_id=pk)
        if likes.exists():
            likes.delete()
        saved_posts = SavedPost.objects.filter(content_type=ct, object_id=pk)
        if saved_posts.exists():
            saved_posts.delete()
        followed_posts = FollowedPost.objects.filter(content_type=ct, object_id=pk)
        if followed_posts.exists():
            followed_posts.delete()
    except Exception as e:
        print str(e)

pre_delete.connect(post_pre_delete_reciever, sender=Post)


class WallPost(models.Model):
    profile = models.ForeignKey(Profile)
    wall_profile=models.ForeignKey(Profile, related_name='wall_post_user')
    welcome=models.BooleanField(default=False)
    content = models.TextField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now=False, auto_now_add=True)
    media = models.FileField(upload_to=media_upload, null=True, blank=True)
    poster = models.ImageField(upload_to=poster_upload, null=True, blank=True)
    like_count = models.PositiveIntegerField(default=0)
    comment_count = models.PositiveIntegerField(default=0)
    views = models.PositiveIntegerField(default=0)
    og = models.OneToOneField(OpenGraph, null=True, blank=True)
    comments = GenericRelation('Comment')
    class Meta:
        ordering=["-timestamp"]

    def __unicode__(self):
        return str(self.profile)+str(self.id)

    @property
    def type(self):
        return 'wall'

    def get_absolute_url(self):
        return reverse("detail", kwargs={"id": self.id, "type_of_post": "wall"})

    @property
    def is_video(self):
        name=self.media.name
        ext = name.split('.')[-1]
        if ext in ['mp4','MP4','3gp','3GP','obb','OBB']:
            return True
        return False

    def image_url(self):
        return '/static/img/welcome-profile.jpg'

def wall_post_pre_delete_reciever(sender, instance, *args, **kwargs):
    try:
        if instance.og:
            instance.og.delete()
        if instance.media:
            path=instance.media.path
            os.remove(path)
        if instance.poster:
            path=instance.poster.path
            os.remove(path)
        ct = ContentType.objects.get_for_model(instance)
        pk = instance.id
        comments = Comment.objects.filter(content_type=ct, object_id=pk)
        if comments.exists():
            comments.delete()
        likes=Like.objects.filter(content_type=ct, object_id=pk)
        if likes.exists():
            likes.delete()
        saved_posts = SavedPost.objects.filter(content_type=ct, object_id=pk)
        if saved_posts.exists():
            saved_posts.delete()
        followed_posts = FollowedPost.objects.filter(content_type=ct, object_id=pk)
        if followed_posts.exists():
            followed_posts.delete()
    except Exception as e:
        print str(e)

pre_delete.connect(wall_post_pre_delete_reciever, sender=WallPost)

class Like(models.Model):
    profile=models.ForeignKey(Profile)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    def __unicode__(self):
        return str(self.profile)

class Comment(models.Model):
    profile=models.ForeignKey(Profile)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    content=models.TextField()
    timestamp=models.DateTimeField(auto_now_add=True, auto_now=False)
    parent=models.ForeignKey("self", null=True, blank=True)
    like_count = models.PositiveIntegerField(default=0)
    # updated = models.DateTimeField(auto_now=True, auto_now_add=False)

    class Meta:
        ordering=["-timestamp"]

    def __unicode__(self):
        return str(self.profile)+" - "+self.content[:10]

    def children(self):
        return Comment.objects.filter(parent=self)

    @property
    def is_parent(self):
        if self.parent is None:
            return True
        return False

def comment_pre_delete_reciever(sender, instance, *args, **kwargs):
    obj=instance.content_object
    obj.comment_count-=1
    obj.save()
    ct = ContentType.objects.get_for_model(instance)
    likes=Like.objects.filter(content_type=ct, object_id=instance.id)
    if likes.exists():
        likes.delete()

pre_delete.connect(comment_pre_delete_reciever, sender=Comment)


"""
user commented on your post
user liked your post
user liked your comment
user followed you
user just joined VestaSocial
"""
class Notification(models.Model):
    profile=models.ForeignKey(Profile)
    profile2=models.ForeignKey(Profile, related_name='related_user')
    title=models.TextField(default='')
    link=models.TextField(default='')
    tag=models.CharField(max_length=1, default='p') # p-post, f-friend profile
    key=models.IntegerField(default=0)
    timestamp=models.DateTimeField(auto_now_add=True, auto_now=False)
    active=models.BooleanField(default=True)
    def __unicode__(self):
        return str(self.profile)+' - '+self.title
    class Meta:
        ordering=['-timestamp']


def ad_upload(instance, filename):
    return 'storage/{0}'.format(filename)

class Advertisement(models.Model):
    title=models.CharField(max_length=30, default='')
    image=models.ImageField(upload_to=ad_upload)
    link=models.TextField(default='')
    description=models.CharField(max_length=240, default="Click on 'find more' to know more about us.")
    def __unicode__(self):
        return self.title

def ad_pre_delete_reciever(sender, instance, *args, **kwargs):
    try:
        if instance.image:
            os.remove(instance.image.path)
    except Exception as e:
        print str(e)

pre_delete.connect(ad_pre_delete_reciever, sender=Advertisement)


class SavedPost(models.Model):
    profile=models.ForeignKey(Profile)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    def __unicode__(self):
        return str(self.profile)
    class Meta:
        ordering=['-id']

class FollowedPost(models.Model):
    profile=models.ForeignKey(Profile)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    def __unicode__(self):
        return str(self.profile)
    class Meta:
        ordering=['-id']
