from django import forms
from .models import Post, WallPost
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import filesizeformat
from PIL import Image
from django.core.files import File

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["content", "media"]
        
    def clean_media(self):
        media = self.cleaned_data.get('media')
        if media and 'FieldFile' not in str(type(media)):
            content_type = media.content_type.split('/')[0]
            if content_type in ['image', 'video']:
                if media._size > 52428800:
                    raise forms.ValidationError(_('Please keep filesize under 50 MB. Current filesize %s') % (filesizeformat(media._size)))
                elif content_type == 'video':
                    filename = str(media)
                    ext = filename.split('.')[-1]
                    if ext not in ['mp4', 'MP4', 'ogg', 'OGG']:
                        raise forms.ValidationError(_('File type is not supported'))
            else:
                raise forms.ValidationError(_('File type is not supported'))
        return media


class WallPostForm(forms.ModelForm):
    class Meta:
        model = WallPost
        fields = ["content", "media"]
        
    def clean_media(self):
        media = self.cleaned_data.get('media')
        if media and 'FieldFile' not in str(type(media)):
            content_type = media.content_type.split('/')[0]
            if content_type in ['image', 'video']:
                if media._size > 52428800:
                    raise forms.ValidationError(_('Please keep filesize under 50 MB. Current filesize %s') % (filesizeformat(media._size)))
                elif content_type == 'video':
                    filename = str(media)
                    ext = filename.split('.')[-1]
                    if ext not in ['mp4', 'MP4', 'ogg', 'OGG']:
                        raise forms.ValidationError(_('File type is not supported'))
            else:
                raise forms.ValidationError(_('File type is not supported'))
        return media

class CommentForm(forms.Form):
    content=forms.CharField()

class ProfilePicForm(forms.Form):
    dp=forms.ImageField()

class CoverPicForm(forms.Form):
    cover=forms.ImageField()