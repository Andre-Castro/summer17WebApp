from django.shortcuts import render

def index(request):
	dict = {}
	return render(request, 'forumSelect/home.html', dict)