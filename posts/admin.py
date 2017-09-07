from django.contrib import admin
from .models import *

@admin.register(Post)
class PostModelAdmin(admin.ModelAdmin):
	list_display = ["profile", "timestamp", "type_of_post", "like_count"]
	list_display_links = ["profile"]
	list_filter = ["timestamp"]
	search_fields = ["content"]
	class Meta:
		model = Post

@admin.register(WallPost)
class WallPostModelAdmin(admin.ModelAdmin):
	list_display = ["profile", "wall_profile", "timestamp", "like_count"]
	list_display_links = ["profile"]
	list_filter = ["timestamp"]
	search_fields = ["content"]
	class Meta:
		model = WallPost


admin.site.register(Comment)
admin.site.register(Like)
admin.site.register(Advertisement)
admin.site.register(Notification)
admin.site.register(OpenGraph)
admin.site.register(SavedPost)
admin.site.register(FollowedPost)