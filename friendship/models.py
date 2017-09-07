from customers.models import Profile
from django.db import models
from django.contrib.auth.models import User

class Follow(models.Model):
	from_user = models.ForeignKey(Profile, related_name='follower')
	to_user = models.ForeignKey(Profile)
	def __unicode__(self):
		return str(self.from_user)+" -> "+str(self.to_user)
	class Meta:
		ordering=['-id']
		unique_together=('from_user', 'to_user')
