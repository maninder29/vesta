from .views import *
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
# /api/posts/
router.register(r'profile', ProfileViewSet)
router.register(r'userphotos', UserPhotosViewSet)
router.register(r'uservideos', UserVideosViewSet)
router.register(r'follow', FollowViewSet)
router.register(r'followers', FollowersViewSet)
router.register(r'following', FollowingViewSet)
router.register(r'myspace/(?P<type_of_post>[\w.@+-]+)',NormalListViewSet)
router.register(r'differential',DoctorListViewSet)
router.register(r'insights',PatientListViewSet)
router.register(r'like/check/(?P<type_of_post>[\w.@+-]+)', CheckPostLikeCommentViewSet)
router.register(r'like/(?P<type_of_post>[\w.@+-]+)', PostLikeViewSet)
router.register(r'comment/like', CommentLikeViewSet)
router.register(r'comment/(?P<type_of_post>[\w.@+-]+)', CommentViewSet)
router.register(r'dp/change', ChangeDpViewSet)
router.register(r'cover/change', ChangeCoverViewSet)
router.register(r'likers/(?P<type_of_post>[\w.@+-]+)', PostLikersViewSet)
router.register(r'comment/likers', CommentLikersViewSet)
router.register(r'notification', NotificationViewSet)
router.register(r'latest/myspace', LatestPostsMyspaceViewSet)
router.register(r'latest/differential', LatestPostsDifferentialViewSet)
router.register(r'latest/insights', LatestPostsInsightsViewSet)
router.register(r'save/(?P<type_of_post>[\w.@+-]+)', SavePostViewSet)
router.register(r'discuss/(?P<type_of_post>[\w.@+-]+)', DiscussPostViewSet)
router.register(r'drawer', DrawerViewSet)

urlpatterns = router.urls