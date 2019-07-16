# encoding: utf-8
import json

from django.http import HttpResponse
from django.views.generic import CreateView, DeleteView, ListView
from .models import Sound
from .response import JSONResponse, response_mimetype
from .serialize import serialize_sound


class SoundCreateView(CreateView):
    model = Sound
    # fields = "__all__"
    fields = ['audio_file']

    def form_valid(self, form):
        self.object = form.save()
        files = [serialize_sound(self.object)]
        data = {'files': files}
        response = JSONResponse(data, mimetype=response_mimetype(self.request))
        response['Content-Disposition'] = 'inline; filename=files.json'
        return response

    def form_invalid(self, form):
        data = json.dumps(form.errors)
        return HttpResponse(content=data, status=400, content_type='application/json')


class jQueryVersionSoundCreateView(SoundCreateView):
    template_name_suffix = '_jquery_sound_form'


class SoundDeleteView(DeleteView):
    model = Sound

    def xget_object(self, queryset=None):
        # pop batmusic- sessie id
        return

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        response = JSONResponse(True, mimetype=response_mimetype(request))
        response['Content-Disposition'] = 'inline; filename=files.json'
        return response


class SoundListView(ListView):
    model = Sound

    def xget_queryset(self):
        # pop batmusic sessie
        return

    def render_to_response(self, context, **response_kwargs):
        files = [ serialize_sound(p) for p in self.get_queryset() ]
        data = {'files': files}
        response = JSONResponse(data, mimetype=response_mimetype(self.request))
        response['Content-Disposition'] = 'inline; filename=files.json'
        return response
