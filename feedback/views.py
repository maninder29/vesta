from django.contrib.auth.decorators import login_required
from django.shortcuts import render,redirect
from django.http import JsonResponse
from .models import *

def feedback(request):
	form=FeedbackForm(request.POST or None)
	if form.is_valid():
		instance=form.save(commit=False)
		instance.save()
		return redirect('home')
	context={
		'form':form,
	}
	return render(request, "initialPages/feedback.html", context)

def privacy(request):
	return render(request, 'initialPages/privacy.html', {})

# @login_required
# def check_review(request, id):
# 	if request.is_ajax():
# 		user=User.objects.get(id=id)
# 		reviewer=request.user
# 		r=Rating.objects.filter(user=user, reviewer=reviewer)
# 		if r.exists():
# 			r=r.first()
# 			return JsonResponse({
# 				'flag': 1,
# 				'rating':str(r.value),
# 				'review':r.content
# 				})
# 		else:
# 			return JsonResponse({'flag': 0})


# @login_required
# def get_all_reviews(request, id):
# 	if request.is_ajax():
# 		user=User.objects.get(id=id)
# 		ratings=Rating.objects.filter(user=user)
# 		listt = []
# 		for i in ratings:
# 			dictionary = {
# 				'dp': str(i.reviewer.profile.dp_url),
# 				'name' : i.reviewer.user.profile.name,
# 				'review' : i.content,
# 				'rating' : str(i.value),
# 			}
# 			listt.append(dictionary)
# 		return JsonResponse({'reviews' : listt})
# 	else:
# 		return redirect('/')
