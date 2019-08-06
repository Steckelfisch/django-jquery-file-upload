# encoding: utf-8
import mimetypes
import re
from django.urls import reverse


def order_name(name):
    """order_name -- Limit a text to 20 chars length, if necessary strips the
    middle of the text and substitute it for an ellipsis.

    name -- text to be limited.

    """
    name = re.sub(r'^.*/', '', name)
    if len(name) <= 20:
        return name
    return name[:10] + "..." + name[-7:]


def serialize(instance, file_attr='file'):
    """serialize -- Serialize a Picture instance into a dict.

    instance -- Picture instance
    file_attr -- attribute name that contains the FileField or ImageField

    """
    obj = getattr(instance, file_attr)
    return {
        'url': obj.url,
        'name': order_name(obj.name),
        'type': mimetypes.guess_type(obj.path)[0] or 'image/png',
        'thumbnailUrl': obj.url,
        'size': obj.size,
        'deleteUrl': reverse('upload-delete', args=[instance.pk]),
        'deleteType': 'DELETE',
    }


def serialize_sound(instance, file_attr='file'):
    """serialize -- Serialize a Sound instance into a dict.

    instance -- Sound instance
    file_attr -- attribute name that contains the FileField or ImageField

    """
    obj = getattr(instance, file_attr)
    return {
        'url': obj.url,
        'name': order_name(obj.name),
        'type': mimetypes.guess_type(obj.path)[0] or 'audio/vnd.wav',
        'imgUrl': obj.url+'.png',
        'thumbnailUrl': obj.url+'.thumbnail.png',
        'size': obj.size,
        'deleteUrl': reverse('session-sound-delete', args=[instance.session_id, instance.pk]),
        'deleteType': 'DELETE',
    }

