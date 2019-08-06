# encoding: utf-8
import json

from django.http import HttpResponse
from django.views.generic import CreateView, DeleteView, ListView
from .models import Sound
from .response import JSONResponse, response_mimetype
from .serialize import serialize_sound

import logging
logger = logging.getLogger(__name__)


class SessionSoundCreateView(CreateView):
    model = Sound
    # fields = "__all__"
    fields = ['file']

    def form_valid(self, form):
        self.object = form.save()
        self.object.session_id = self.kwargs['session_pk']  # pak session_pk
        self.object.save()
        self.object.move_to_session_dir()
        img_path = self.object.create_spectrogram()
        self.object.create_thumbnail()
        logger.debug("spectrogram: "+img_path)
        files = [serialize_sound(self.object)]
        data = {'files': files}
        response = JSONResponse(data, mimetype=response_mimetype(self.request))
        response['Content-Disposition'] = 'inline; filename=files.json'
        return response

    def form_invalid(self, form):
        data = json.dumps(form.errors)
        return HttpResponse(content=data, status=400, content_type='application/json')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['session_pk'] = self.kwargs['session_pk']
        return context

#class jQueryVersionSoundCreateView(SessionSoundCreateView):
#    template_name_suffix = '_jquery_sound_form'


class SessionSoundDeleteView(DeleteView):
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


class SessionSoundListView(ListView):
    model = Sound

    def get_queryset(self):
        return Sound.objects.filter(session=self.kwargs['session_pk'])

    def render_to_response(self, context, **response_kwargs):
        files = [ serialize_sound(p) for p in self.get_queryset() ]
        data = {'files': files}
        response = JSONResponse(data, mimetype=response_mimetype(self.request))
        response['Content-Disposition'] = 'inline; filename=files.json'
        return response

    # def get_context_data(self, *, object_list=None, **kwargs):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['session_pk'] = self.kwargs['session_pk']
        return context
