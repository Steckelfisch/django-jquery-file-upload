# encoding: utf-8
from django.contrib.auth.decorators import login_required
from django.urls import path
from django.conf.urls import include
from django.conf import settings
from fileupload.views import (
        BasicVersionCreateView, BasicPlusVersionCreateView,
        jQueryVersionCreateView, AngularVersionCreateView,
        PictureCreateView, PictureDeleteView, PictureListView,
        )

# from fileupload.sound_views import SoundCreateView, SoundDeleteView, SoundListView
from fileupload.session_sound_views import SessionSoundCreateView, SessionSoundDeleteView, SessionSoundListView
from fileupload.session_views import SessionCreateView, SessionUpdateView, SessionListView
from fileupload.session_views import SessionLocationRecorderView, SessionLocationRecorderUpdateView
from fileupload.session_sound_archive_views import SoundArchiveCreateView

urlpatterns = [

    path('basic/', BasicVersionCreateView.as_view(), name='upload-basic'),
    path('basic/plus/', BasicPlusVersionCreateView.as_view(), name='upload-basic-plus'),
    path('new/', PictureCreateView.as_view(), name='upload-new'),
    path('angular/', AngularVersionCreateView.as_view(), name='upload-angular'),
    path('jquery-ui/', jQueryVersionCreateView.as_view(), name='upload-jquery'),
    path('delete/<int:pk>', PictureDeleteView.as_view(), name='upload-delete'),
    path('view/', PictureListView.as_view(), name='upload-view'),

    path('session/new/', login_required(SessionCreateView.as_view()), name='session-new'),
    path('session/<int:pk>/', SessionUpdateView.as_view(), name='session-view'),
    path('session/<int:pk>/location-recorder-old/',
         login_required(SessionLocationRecorderView.as_view()), name='session-location-recorder-old'),
    path('session/<int:pk>/location-recorder/',
         login_required(SessionLocationRecorderUpdateView.as_view()), name='session-location-recorder'),
    path('session/<int:pk>/update/', login_required(SessionUpdateView.as_view()), name='session-update'),
    path('session/', SessionListView.as_view(), name='session-list'),

    path('session/<int:session_pk>/sound/upload/', SessionSoundCreateView.as_view(), name='session-sound-new'),
    path('session/<int:session_pk>/sound/<int:pk>/delete/',
         login_required(SessionSoundDeleteView.as_view()),
         name='session-sound-delete'),
    # path('session/<int:session_pk>/sound-archive-upload/', SessionSoundArchiveView.as_view(), name='session-sound-archive'),
    path('session/<int:session_pk>/sound-archive-upload/', SoundArchiveCreateView.as_view(),
         name='session-sound-archive-new'),
    path('session/<int:session_pk>/sound/', SessionSoundListView.as_view(), name='session-sound-list-view'),

    #path('sound/new/', SoundCreateView.as_view(), name='upload-sound'),
    #path('sound/<int:pk>/delete/', SoundDeleteView.as_view(), name='upload-sound-delete'),
    #path('sound/view/', SoundListView.as_view(), name='upload-sound-list-view'),

]


if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),

        # For django versions before 2.0:
        # url(r'^__debug__/', include(debug_toolbar.urls)),

    ] + urlpatterns