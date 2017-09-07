from django.conf.urls import url
from .views import *
# feedback/
urlpatterns = [
	url(r'^$', feedback, name='feedback'),
	url(r'^privacy/$', privacy, name='privacy'),
	# url(r'^check_review/(?P<id>\d+)/$', check_review, name='check_review'),
	# url(r'^get_all_reviews/(?P<id>\d+)/$', get_all_reviews, name='get_all_reviews'),
]