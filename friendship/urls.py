from django.conf.urls import url
from .views import *

urlpatterns=[
	# url(r'send/(?P<id>\d+)/', send_friend_request, name='send_friend_request'),
	# url(r'accept/(?P<id>\d+)/', accept_friend_request, name='accept_friend_request'),
	# url(r'reject/(?P<id>\d+)/', reject_friend_request, name='reject_friend_request'),
	# url(r'remove/(?P<id>\d+)/', remove_friend, name='remove_friend'),
	# url(r'acceptRequest/(?P<id>\d+)/', accept_friend, name='accept_friend'),
	url(r'^follow/(?P<id>\d+)/$', follow, name='follow'),
	url(r'^unfollow/(?P<id>\d+)/$', unfollow, name='unfollow'),
	url(r'^remove_follower/(?P<id>\d+)/$', remove_follower, name='remove_follower'),
	url(r'^followers/(?P<id>\d+)/$', all_followers, name='all_followers'),
	url(r'^following/(?P<id>\d+)/$', all_following, name='all_following'),
]