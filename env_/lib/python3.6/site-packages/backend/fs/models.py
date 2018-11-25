import os, shutil, time
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.db import models
from django.http import HttpResponse
from django.contrib.auth.models import User

from backend.util.views import unique_repeat
from slugify import slugify


class OverwriteStorage( FileSystemStorage ):
    def get_available_name( self, name ):
        if os.path.exists( self.path( name ) ):
            os.remove( self.path( name ) )
        return name


def get_file_upload_path( instance, filename ):
	if not instance.alias:
		print '[WARNING]  File alias calculated by NULL owner'

		name, alias, repeat, ext, t = get_alias( filename, None )
		instance.name = name
		instance.alias = alias
		instance.repeat = repeat
		instance.ext = instance.ext
		instance.type = t
		# instance.save()

	return instance.path + instance.alias + '.' + instance.ext


def get_alias( name, owner, *args ):
	# process type
	ext = name.split( '.' )[ -1 ]
	if ext in settings.MAP_FILE:
		t = settings.MAP_FILE[ ext ]
	else:
		t = 'Document'

	# process name
	alias, repeat = unique_repeat( File, name[ :-1*len( ext )-1 ], *args, owner = owner )
	return name, alias, repeat, ext, t


class File( models.Model ):
	id = models.AutoField( primary_key = True )
	alias = models.CharField( max_length = 512 )
	repeat = models.IntegerField( default = 0 )

	name = models.CharField( max_length = 512 )
	ext = models.CharField( max_length = 32 )
	path = models.CharField( max_length = 512 )
	type = models.CharField( max_length = 32 )
	mime = models.CharField( max_length = 512, default = 'application/force-download' )

	file = models.FileField( upload_to = get_file_upload_path, max_length = 512, storage = OverwriteStorage() )
	owner = models.ForeignKey( User, related_name = 'owner_files', on_delete = models.SET_NULL, null = True )


	def edit( self, f ):
		if f:
			if os.path.exists( self.path + self.alias + '.' + self.ext ):
				try:
					o = self.owner.get_profile()
					o.usedstg -= self.file.size
				except: pass
				os.remove( self.path + self.alias + '.' + self.ext )

			name, alias, repeat, ext, t = get_alias( f.name, self.owner, ~models.Q( id = self.id ) )

			self.name = name
			self.type = t
			self.file = f
			self.mime = f.content_type
			self.save()

			try:
				p = self.owner.get_profile()
				p.usedstg += self.file.size
				p.save()
			except: pass


	def download( self, request, **kwargs ):
		response = HttpResponse( content_type = self.mime )
		response[ 'Content-Length' ] = self.file.size
		response[ 'Content-Disposition' ] = 'filename=%s' % self.name
		response[ 'Content-Type' ] = self.mime
		response.write( open( self.path + self.alias + '.' + self.ext, "rb" ).read() )
		return response


	def url( self ):
		return self.path[ len( settings.MEDIA_ROOT ): ] + self.alias + '.' + self.ext


	@staticmethod
	def create( owner, f, prefix = False, *args, **kwargs ):
		try:
			p = owner.get_profile()
			if p.usedstg >= p.maxstg:
				return None
		except: pass

		name, alias, repeat, ext, t = get_alias( f.name, owner )

		# create file
		fl = File.objects.create( name = name, alias = alias, repeat = repeat, ext = ext, file = f, mime = f.content_type, owner = owner,
			path = settings.MEDIA_ROOT + ( prefix if prefix else '' ) + owner.username + time.strftime( "/%Y/%m/%d/" ), type = t )

		# track storage
		try:
			p = owner.get_profile()
			p.usedstg += fl.file.size
			p.save()
		except: pass
		
		return fl


	@staticmethod
	def remove( f, *args, **kwargs ):
		if f:
			if os.path.exists( f.path + f.alias ):
				try:
					p = self.owner.get_profile()
					p.usedstg -= f.file.size
					p.save()
				except: pass

				os.remove( f.path + f.alias + '.' + f.ext )

			f.delete()

