# encoding: utf-8
from django.urls import path
from fileupload.views import (
        BasicVersionCreateView, BasicPlusVersionCreateView,
        jQueryVersionCreateView, AngularVersionCreateView,
        PictureCreateView, PictureDeleteView, PictureListView,
        )

from fileupload.sound_views import SoundCreateView, SoundDeleteView, SoundListView


urlpatterns = [
    path('basic/', BasicVersionCreateView.as_view(), name='upload-basic'),
    path('basic/plus/', BasicPlusVersionCreateView.as_view(), name='upload-basic-plus'),
    path('new/', PictureCreateView.as_view(), name='upload-new'),
    path('angular/', AngularVersionCreateView.as_view(), name='upload-angular'),
    path('jquery-ui/', jQueryVersionCreateView.as_view(), name='upload-jquery'),
    path('delete/<int:pk>', PictureDeleteView.as_view(), name='upload-delete'),
    path('view/', PictureListView.as_view(), name='upload-view'),

    #path('session/<int:session_pk>/sound/new/', SoundCreateView.as_view(), name='session-sound-new'),
    #path('session/<int:session_pk>/sound/<int:sound_pk>/delete/', SoundCreateView.as_view(), name='session-sound-delete'),
    #path('sound/<int:session_pk>/view/', SoundListView.as_view(), name='session-sound-view'),

    path('sound/new/', SoundCreateView.as_view(), name='upload-sound'),
    path('sound/<int:pk>/delete/', SoundDeleteView.as_view(), name='upload-sound-delete'),
    path('sound/view/', SoundListView.as_view(), name='upload-sound-view'),

]
