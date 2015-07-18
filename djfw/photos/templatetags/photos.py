from django.utils.translation import ugettext_lazy as _
from django.shortcuts import get_object_or_404
from django import template
from djfw.tinymce.bbcodes import bbcode_to_html
from djfw.photos.models import Photo, PhotoAlbum

register = template.Library()

photo_codes_list = {}

@register.filter
def photolize(value):
    return bbcode_to_html(value, codes_list={}, simple_codes_list=photo_codes_list)

def photo(tagname, param):
    if not param:
        return None
    try:
        param = int(param)
        photo = get_object_or_404(Photo, id=param)
    except:
        return unicode(_('[photo not found]'))
    return '<div class="big_photo"><img id="photo%s" src="%s" alt="%s" /></div>' % (param, 
                                                                         photo.image.url, 
                                                                         photo.title)
def photosmall(tagname, param):
    if not param:
        return None
    try:
        param = int(param)
        photo = get_object_or_404(Photo, id=param)
    except:
        return unicode(_('[photo not found]'))
    div = '<div id="photo%s" class="small_photo">' % (param,)
    img = '<img src="%s" /></a>' % (photo.thumbnail.url,)
    a = '<a href="%s" rel="lightbox[smallphotos]" title="%s">' % (photo.image.url, photo.title,) 
    return div + a + img + '</a></div>'

def photoalbum(tagname, param):
    if not param:
        return None
    try:
        param = int(param)
        album = get_object_or_404(PhotoAlbum, id=param)
    except:
        return unicode(_('[photo not found]'))
    result = '<div id="album%s">' % (param, )
    photos = album.photos.all()
    for photo in photos:
        photo.thumbnail
        if photo.image and photo.thumbnail:
            result += '<div id="photo%s" class="small_photo">' % (photo.id, )
            result += '<a href="%s" rel="lightbox[album%s]" title="%s">' % (photo.image.url, param, photo.title,)
            result += '<img src="%s" /></a></div>' % (photo.thumbnail.url,)
    return result + '</div>'

photo_codes_list['photo'] = photo
photo_codes_list['photosmall'] = photosmall
photo_codes_list['photoalbum'] = photoalbum