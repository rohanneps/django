from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.conf import settings
from wsgiref.util import FileWrapper
import mimetypes
import os

def home(request):
	if not request.user.is_authenticated:
		return HttpResponseRedirect(settings.LOGOUT_REDIRECT_URL)
	else:
		return render(request, 'home.html')




def download_sample_template(request):
	if not request.user.is_authenticated:
		return HttpResponseRedirect(settings.LOGOUT_REDIRECT_URL)
	else:
		file_path = os.path.join(settings.SAMPLE_TEMPLATE_DIR, settings.SAMPLE_TEMPLATE_FILE)	
		file_wrapper = FileWrapper(open(file_path,'rb'))
		file_mimetype = mimetypes.guess_type(file_path)
		response = HttpResponse(file_wrapper, content_type=file_mimetype )
		response['X-Sendfile'] = file_path
		response['Content-Length'] = os.stat(file_path).st_size
		response['Content-Disposition'] = 'attachment; filename=%s' % (settings.SAMPLE_TEMPLATE_FILE) 
		return response