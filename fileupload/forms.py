# -*- coding: utf-8 -*-
import django.forms as forms


class SessionSoundArchiveUploadForm(forms.Form):
    archive_file = forms.FileField(label='Achive File', required=True)