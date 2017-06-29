from django.shortcuts import render

def index(request):
	#file = open('')

	#list elements represent: [name, num, num, num, num]
	dict = {
		'forums':[
			["Wilders", "1002"], 
			["Offcomm", "2002"],
			["HackThisSite", "3002"],
		],
		'name':"test",
	}
	return render(request, 'forumSelect/home.html', dict)