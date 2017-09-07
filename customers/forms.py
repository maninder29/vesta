from django import forms
from .models import *

class RegisterForm(forms.Form):
	name = forms.CharField(required=True, max_length=60)
	email = forms.CharField(required=True, max_length=60)
	type_of_user = forms.CharField(required=True, max_length=20)
	dp = forms.FileField(required=False)
	def clean_name(self, *args, **kwargs):
		name=self.cleaned_data.get('name')
		if not name:
			raise forms.ValidationError('This field is required')
		return name
	def clean_email(self, *args, **kwargs):
		email=self.cleaned_data.get('email')
		if not email:
			raise forms.ValidationError('This field is required')
		return email
	def clean_type_of_user(self, *args, **kwargs):
		type_of_user=self.cleaned_data.get('type_of_user')
		if not type_of_user:
			raise forms.ValidationError('This field is required')
		elif type_of_user not in ['doctor', 'student', 'fitness_enthusiast', 'patient']:
			raise forms.ValidationError('Invalid type of user')
		return type_of_user