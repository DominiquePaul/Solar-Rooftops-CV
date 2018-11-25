from django import template
import re

register = template.Library()


# get value of key in table
def value( table, key ):
	if table:
		return table.get( key, '' )
	else: return None
	
register.filter( 'value', value )


# get attribute of object
def attr( obj, key ):
	return getattr( obj, key )
	
register.filter( 'attr', attr )


# call function
def call( f, x ):
	return f( x )
	
register.filter( 'call', call )


# strip function
def strip( src, x = '&nbsp;' ):
	return src.replace( x, ' ' )
	
register.filter( 'strip', strip )


def hms( num ):
	s = num % 60
	num = num/60
	m = num % 60
	num = num/60
	h = num % 60

	if h:
		return "%.2d:%.2d:%.2d" % ( h, m, s )
	else:
		return "%.2d:%.2d" % ( m, s )
	
register.filter( 'hms', hms )

