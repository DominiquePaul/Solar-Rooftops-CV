import json, re, urllib2, base64, StringIO

from django.conf import settings
from django.db import models
from django.shortcuts import render_to_response
from django.template.loader import get_template
from django.template import RequestContext
from django.http import HttpResponse, Http404

from slugify import slugify
from PIL import Image


def render( request, data = None, tmpl = 'home.html', error = None, type = 'html', html = False, jade = False, *args, **kwargs ):
	if data is None: data = {}
	data[ 'settings' ] = settings
	data[ 'error' ] = error

	if html: tmpl += '.html'
	if jade: tmpl += '.jade'

	if type == 'json':
		t = get_template( tmpl )
		html = t.render( RequestContext( request, data ) )
		return HttpResponse( json.dumps( { 'html' : html } ), mimetype='text/plain' )
	else:
		return render_to_response( tmpl, data, context_instance = RequestContext( request ) )


def image_process( fi, fo, max_width = 1920, square = False ):
	if fi:
		img = Image.open( fi )
		w, h = image.size

		if square:
			if w > h:
				diff = int((w - h) / 2)
				image = image.crop((diff, 0, w - diff, h))
				w = h
			else:
				diff = int((h - w) / 2)
				image = image.crop((0, diff, w, h - diff))
				h = w
        
		if image.mode != "RGB":
			image = image.convert("RGB")

		if w > max_width:
			h = h * max_width / w
			w = max_width
			image = image.resize( ( w, h ), Image.ANTIALIAS )

		image.save( fo, format = 'PNG' )
		fo.close()


def file_encode( f ):
	if f:
		return base64.b64encode( f.read() )
	return ''


def find( cls, **kwargs ):
	try:
		return cls.objects.get( **kwargs )
	except cls.DoesNotExist:
		return None


def unique( cls, name, **kwargs ):
	alias = slugify( name )
	try:
		cls.objects.get( alias = alias, **kwargs )
		alias = alias + '-' + str( cls.objects.filter( **kwargs ).count() )
	except cls.DoesNotExist:
		pass
	
	return alias


def unique_repeat( cls, name, *args, **kwargs ):
	alias = slugify( name )
	last = cls.objects.filter( alias__startswith = alias, *args, **kwargs ).order_by( '-repeat' )[ :1 ]
	if last:
		repeat = last[ 0 ].repeat + 1
		alias = alias + '-' + str( repeat )
		return alias, repeat
	return alias, 1


def reorder( request, cls ):
	ids = request.POST.getlist( 'orderid' )
	rank = 0
	for id in ids:
		obj = cls.objects.get( id = int( id ) )
		obj.rank = rank
		obj.save()
		rank += 1


def delete( request, cls ):
	for id in request.POST.getlist( 'deleteid' ):
		try:
			obj = cls.objects.get( id = int( id ) )
			obj.delete()
		except cls.DoesNotExist:
			pass


def get_class( kls ):
	parts = kls.split('.')
	module = ".".join(parts[:-1])
	m = __import__( module )
	for comp in parts[1:]:
		m = getattr(m, comp)            
	return m


def concrete( obj ):
	try:
		return getattr( obj, obj.type )
	except AttributeError:
		return None


def map_list( l, key ):
	m = {}
	for i in l:
		m[ getattr( i, key ) ] = i
	return m


def matrix( l, row, col, value ):
	m = {}
	for i in l:
		r = getattr( l, row )
		c = getattr( l, col )

		r = m.get( r, {} )
		r[ c ] = getattr( l, value )

	return m


def letter( string ):
	if string:
		string = string[ 0 ].capitalize()
		n = ord( string )
		if n > 64 and n < 91:
			return string[ 0 ]
	return '1'


def total_seconds( delta ):
	return delta.days * 24 * 60 * 60 + delta.seconds


def incr( obj, attr, val = 1 ):
	setattr( obj, attr, models.F( attr ) + val )
	obj.save()
	return obj.__class__.objects.get( id = obj.id )


def decr( obj, attr, val = 1 ):
	setattr( obj, attr, models.F( attr ) - val )
	obj.save()
	return obj.__class__.objects.get( id = obj.id )

