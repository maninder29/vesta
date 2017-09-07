from __future__ import unicode_literals
# from customers.models import Profile
from django.db import models
from django import forms
from django.contrib.auth.models import User

CHOICES = (
	(u'1', u'User verification'),
	(u'2', u'Bug report'),
	(u'3', u'Suggestion'),
	(u'4', u'Review')
)

class Feedback(models.Model):
	name=models.CharField(max_length=50,default='')
	email=models.CharField(max_length=50,default='')
	phone=models.CharField(max_length=15,default='')
	content=models.TextField(default='')
	category=models.CharField(max_length=1, choices=CHOICES, default='1')
	active=models.BooleanField(default=True)
	def __unicode__(self):
		if self.category == '1':
			return "User verification"
		elif self.category == '2':
			return "Bug report"
		elif self.category == '3':
			return "Suggestion"
		else:
			return "Review"


class FeedbackForm(forms.ModelForm):
	class Meta:
		model=Feedback
		fields=['name', 'email', 'phone', 'content', 'category']


# class Rating(models.Model):
# 	profile=models.ForeignKey(Profile)
# 	reviewer=models.ForeignKey(Profile, related_name='user_who_rated')
# 	value=models.PositiveIntegerField(default=1)
# 	content=models.CharField(max_length=160, null=True, blank=True)
# 	class Meta:
# 		unique_together = ('profile', 'reviewer')
# 	def __unicode__(self):
# 		return self.profile.name + "-" + str(self.value)

# class RatingForm(forms.ModelForm):
# 	class Meta:
# 		model=Rating
# 		fields=['value', 'content']