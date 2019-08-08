# encoding: utf-8
import json

from django.http import HttpResponseRedirect
from django.shortcuts import redirect, reverse
from django.views.generic import CreateView, DeleteView, ListView, FormView
from .models import SoundArchive


class SoundArchiveCreateView(CreateView):
    model = SoundArchive
    fields = ['file']

    def get_success_url(self):
        return reverse('session-sound-archive', kwargs={'session_pk': self.object.id})

    def form_valid(self, form):
        self.object = form.save()
        self.object.session_id = self.kwargs['session_pk']  # verbind aan sessie
        self.object.save()
        # Batmusic Processing
        self.object.move_to_session_dir()

        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['session_pk'] = self.kwargs['session_pk']
        context['sound_archive_list'] = SoundArchive.objects.filter(session_id=context['session_pk'])
        return context
