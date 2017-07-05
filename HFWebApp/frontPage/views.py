from django.shortcuts import render
import re
import os
                
def index(request):
	dict = {}
	dict["names"] = []
	file = open (os.path.join(os.path.dirname(os.path.realpath(__file__))+ '/templates/frontPage/includes/forumInfo.dat'), 'r')
	lines = re.split(r'\n', file.read())
	name = ""
	i = -1
	for word in lines:
		if word[0] == '-':
			name = word[1:-1]
			dict["names"].append([re.sub('[\s\'.,\/#!$%\^&\*;:{}=\-_`~()]','', name),name,])
			i += 1
		elif word[0] == '&' and name != "":
			dict["names"][i].append(word[1:])
		elif name != "": #check to make sure there are no incorrectly placed lines before the first forum name
			words = ['$',]
			word = re.sub('\$', '', word)
			words = words + word.split(':')
			dict["names"][i].append(words)

	return render(request, 'frontPage/home.html', dict)
	#return HttpResponse("<h3> IP Extractor Tool </h3>")