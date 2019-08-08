#!/bin/bash


# echo "CHANGE DJANGO_SETTINGS_MODULE to propper settings file and remove \"exit\""
# exit

export DJANGO_SETTINGS_MODULE=django-jquery-file-upload.settings
# export SECRET_KEY='1&ga4)8q+ji5k6z9ok@y*gslko573$ygo7%#(8bjag&pftpcd5'



env | grep 'DJANGO\|SECRET_KEY'

