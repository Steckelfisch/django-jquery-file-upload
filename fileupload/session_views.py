# encoding: utf-8
import json

from django.http import HttpResponseRedirect
from django.shortcuts import redirect, reverse
from django.views.generic import CreateView, UpdateView, ListView, DetailView, FormView
from django.views.generic.detail import SingleObjectMixin
from django.views.generic import FormView
from .models import BatMusicSession
from .response import JSONResponse, response_mimetype
from .serialize import serialize_sound

import logging
logger = logging.getLogger(__name__)


class SessionListView(ListView):
    model = BatMusicSession

class SessionDetailView(DetailView):
    model = BatMusicSession
    fields = ['name', 'description',
              'start_date_time', 'end_date_time',
              'recordingtime_in_dst', 'daylight_saving_correction']  # "__all__"

class SessionCreateView(CreateView):
    model = BatMusicSession
    fields = ['name', 'description',
              'start_date_time', 'end_date_time',
              'recordingtime_in_dst', 'daylight_saving_correction']  # "__all__"

    def get_success_url(self):
        return reverse('session-update', kwargs={'pk': self.object.id})

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        # self.object.check_data_needs_dst_check()
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())

class SessionUpdateView(UpdateView):
    model = BatMusicSession
    fields = ['name', 'description',
              'start_date_time', 'end_date_time',
              'recordingtime_in_dst', 'daylight_saving_correction']  # "__all__"

    def get_success_url(self):
        return reverse('session-update', kwargs={'pk': self.object.id})

class SessionLocationRecorderView(SingleObjectMixin, FormView):
    model = BatMusicSession


class SessionLocationRecorderUpdateView(UpdateView):
    model = BatMusicSession
    fields = ['location',
              # 'recorder' ,
              'recorder_text']
    template_name = 'fileupload/location_recorder_form.html'

    def get_success_url(self):
        return reverse('session-location-recorder', kwargs={'pk': self.object.id})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['session_pk'] = self.object.id #  self.kwargs['pk']
        return context


