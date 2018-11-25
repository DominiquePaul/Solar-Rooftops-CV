from django.conf import settings
from django.http import HttpResponse, Http404

from backend.fs.models import File
from backend.util.views import render


def create_file( request, key = 'file', **kwargs ):
	f = request.FILES.get( key, None ) if request.FILES else None
	if not f: return -1

	try:
		o = request.user.get_profile()
		if f and o.maxstg <= o.usedstg:
			return 0
	except: pass

	return File.create( owner = request.user, f = f, prefix = 'embeds/' )


def embed_image( request, **kwargs ):
	tmpl = 'fs/image.html'
	data = {}

	f = create_file( request, **kwargs )

	if not request.user.is_authenticated():
		return Http404
	
	if f == -1:
		return Http404

	if f == 0:
		return render( request, data = data, tmpl = tmpl, error = 'File Storage Space Exceeded', type = 'json' )

	if not f:
		return render( request, data = data, tmpl = tmpl, error = 'Error Storing File', type = 'json' )

	data[ 'src' ] = f.url()
	return render( request, data = data, tmpl = tmpl, type = 'json' )


def embed_image_tinymce( request, **kwargs ):
	tmpl = 'fs/image-tinymce.html'
	data = {}

	f = create_file( request, **kwargs )

	if not request.user.is_authenticated():
		return Http404
	
	if f == -1:
		return Http404

	if f == 0:
		return render( request, data = data, tmpl = tmpl, error = 'File Storage Space Exceeded' )

	if not f:
		return render( request, data = data, tmpl = tmpl, error = 'Error Storing File' )

	data[ 'src' ] = f.url()
	return render( request, data = data, tmpl = tmpl )

