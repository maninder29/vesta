from django.conf.urls import url,include
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_jwt.views import obtain_jwt_token
from customers.views import thumbnail
from django.contrib.auth import views as auth_views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^accounts/', include('allauth.urls')),
    url(r'^auth/', include('rest_framework_social_oauth2.urls')),
    url(r'^', include('customers.urls')),
    url(r'^posts/', include('posts.urls')),
    url(r'^friends/', include('friendship.urls')),
    url(r'^feedback/', include('feedback.urls')),
    url(r'^api-token-auth/', obtain_jwt_token),
    url(r'^api/', include('customers.api.urls')),
    url(r'^api/posts/', include('posts.api.urls')),
    url(r'^thumbnail', thumbnail, name = 'thumbnail'),
    url(r'^logout/$', auth_views.logout, name='logout'),
]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
