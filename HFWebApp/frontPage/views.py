from django.shortcuts import render
from django.http import HttpResponse

def index(request):
	return render(request, 'frontPage/home.html')
	#return HttpResponse("<h3> IP Extractor Tool </h3>")