from django.conf.urls import url
from .views import *
# posts/
urlpatterns = [
	url(r'^differential/$', list_doctor, name='list_doctor'),
	url(r'^mySpace/$', list_normal, name='list_normal'),
	url(r'^insights/$', list_patient, name='list_patient'),

	url(r'^new_mySpace_list/(?P<id>\d+)/$', new_myspace_list, name='new_myspace_list'),
	url(r'^new_differential_list/(?P<id>\d+)/$', new_differential_list, name='new_differential_list'),
	url(r'^new_insights_list/(?P<id>\d+)/$', new_insights_list, name='new_insights_list'),

	url(r'^profile/(?P<id>\d+)/$', profile, name='profile'),
	# url(r'^new_profile_list/(?P<id>\d+)/(?P<user_id>\d+)/$', new_profile_list, name='new_profile_list'),

	url(r'^photos/(?P<id>\d+)/$', all_photos, name='all_photos'),
	url(r'^videos/(?P<id>\d+)/$', all_videos, name='all_videos'),

	url(r'^notification/deactivate/(?P<id>\d+)/$', deactivate_notification, name='deactivate_notification'),
	url(r'^notification/all/$', all_notifications, name='all_notifications'),
	url(r'^notification/all/read/$', mark_all_notifications_read, name='mark_all_notifications_read'),
	
	url(r'^all_users/$', all_users, name='all_users'),
	url(r'^search_user/$', search_user, name='search_user'),
	url(r'^comment/(?P<id>\d+)/edit/$', comment_update, name='comment_update'),
	url(r'^comment/(?P<id>\d+)/delete/$', comment_delete, name='comment_delete'),
	url(r'^comment/(?P<id>\d+)/like/$', comment_like, name='comment_like'),
	url(r'^discussion/$', followed_posts, name='followed_posts'),
	url(r'^saved/$', saved_posts, name='saved_posts'),
	
	url(r'^(?P<type_of_post>[\w.@+-]+)/(?P<id>\d+)/$', post_detail, name='detail'),
	url(r'^(?P<type_of_post>[\w.@+-]+)/(?P<id>\d+)/edit/$', post_update, name='update'),
	url(r'^(?P<type_of_post>[\w.@+-]+)/(?P<id>\d+)/delete/$', post_delete, name='delete'),
	url(r'^(?P<type_of_post>[\w.@+-]+)/(?P<id>\d+)/like/$', post_like, name='like'),
	url(r'^(?P<type_of_post>[\w.@+-]+)/(?P<id>\d+)/save/$', save_post, name='save_post'),
	url(r'^(?P<type_of_post>[\w.@+-]+)/(?P<id>\d+)/follow/$', follow_post, name='follow_post'),
	url(r'^(?P<type_of_post>[\w.@+-]+)/(?P<id>\d+)/likers/$', get_post_likers, name='get_post_likers'),
]