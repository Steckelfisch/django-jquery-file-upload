# encoding: utf-8
import logging

import os, shutil
from subprocess import call
from PIL import Image

from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

logger = logging.getLogger(__name__)

YES_NO_UNKOWN_CHOICES = (
    ('Y', _('Yes')),
    ('N', _('No')),
    ('U', _('Unknown')),
)

YES_NO_CHOICES = (
    ('', _('Make a choice')),
    ('Y', _('Yes')),
    ('N', _('No')),
)

BOOLEAN_YES_NO_CHOICES = (
    ('', _('Make a choice')),
    (True, _('Yes')),
    (False, _('No')),
)

DATA_ELEMENT_CHOICES = (
    (1, _('Location')),
    (2, _('Session')),
    (3, _('Recorder')),
    (4, _('Sound')),
)

ATTRIBUTE_VALUE_TYPE_CHOICES = (
    (0, _('FreeFormat (string)')),
    (1, _('String')),
    (2, _('Integer')),
    (3, _('Date')),
    (4, _('Time')),
    (5, _('Date/Time')),
)

SESSION_OPEN = 'OPEN'
SESSION_CLOSED = 'CLOS'
SESSION_PUBLIC = 'PUBL'
SESSION_STATUS_CHOICES = (
    (SESSION_OPEN,   "Session under Development" ),
    #(SESSION_CLOSED, ""Session ready for Publication" ),
    (SESSION_PUBLIC, "Session Published" ),
)
SESSION_STATUS_FILTER_CHOICES = SESSION_STATUS_CHOICES
SESSION_STATUS_FILTER_CHOICES = (
    ('', "All Sessions"),
    (SESSION_OPEN,   "Session under Development" ),
    #(SESSION_CLOSED, "Session ready for Publication" ),
    (SESSION_PUBLIC, "Session Published" ),
)


class BatMusicSession(models.Model):
    # Hub class for BatMusic
    # Session holds data for a period of measurements for a specific location.
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    status = models.CharField('Status', max_length=5,
                                        choices=SESSION_STATUS_CHOICES,
                                        default=SESSION_OPEN)

    name = models.CharField(max_length=50, unique=True)
    description = models.CharField(max_length=200)
    # recorder = models.ForeignKey('Recorder', on_delete=models.SET_NULL, null=True, blank=True)
    recorder_text = models.CharField(_("Text alternative for 'Recorder'"),
                                     max_length=100, null=True, blank=True)
    start_date_time = models.DateTimeField()
    end_date_time = models.DateTimeField()

    # research_goal
    # research_method

    # http://stackoverflow.com/questions/2532729/daylight-saving-time-and-time-zone-best-practices
    # if true and during DST, recording timings have been corrected. (one hour is added)
    # if false and during DST, all recordings are in non DST, and should be corrected by batmusic

    recordingtime_in_dst = models.BooleanField(_('Recordingperiod has DST'), default=False)

    # if true, user has applied DST correction
    # if false, Batmusic will apply DST correction when processing the uploaded data
    daylight_saving_correction = models.BooleanField(_('DST Correction Applied (by user)'), default=False)

    # location = models.ForeignKey('Location', on_delete=models.SET_NULL, null=True)

    # creation_date_time = models.DateTimeField(auto_now_add=True)
    last_upload_trigger_date_time = models.DateTimeField(_('Last time Files have been uploaded'),
                                                         null=True, blank=True)

    last_upload_mtime = models.IntegerField(_('Last max mtime Uploaded Item'), default=0)

    class Meta:
        verbose_name = _("BatMusic Session")
        verbose_name_plural = _("BatMusic Sessions")

    def __str__(self):
        return self.name

    def get_data_dir(self):
        # logger.error("get_data_dir: "+str(self.id))
        # assert (not self.id), "BatMusicSession has no id yet"
        return os.path.join(settings.FILE_STORE_DIR,
                            settings.SESSION_DATA_DIR,
                            str(self.id))



class Picture(models.Model):
    """This is a small demo using just two fields. The slug field is really not
    necessary, but makes the code simpler. ImageField depends on PIL or
    pillow (where Pillow is easily installable in a virtualenv. If you have
    problems installing pillow, use a more generic FileField instead.

    """
    file = models.ImageField(upload_to="pictures")
    slug = models.SlugField(max_length=50, blank=True)

    def __str__(self):
        return self.file.name

    # @models.permalink
    def get_absolute_url(self):
        # return ('upload-new', )
        return reverse('upload-new', args=(self.slug,))

    def save(self, *args, **kwargs):
        self.slug = self.file.name
        super(Picture, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """delete -- Remove to leave file."""
        self.file.delete(False)
        super(Picture, self).delete(*args, **kwargs)


class Sound(models.Model):
    '''
    check: http://stackoverflow.com/questions/6194901/django-audio-file-validation
    '''

    session = models.ForeignKey(BatMusicSession, on_delete=models.CASCADE, null=True, blank=True)

    recording_date_time = models.DateTimeField(_('Recording Date-Time'), null=True, blank=True)


    night_number = models.IntegerField(_('Night Number'), default=0, blank=True) # will be set on publishing the session
    in_night_index = models.IntegerField(_('Index in Night'), default=0, blank=True) # will be set on publishing the session
    #in_session_index = models.IntegerField(_('Index in Session'), default=0)

    alias = models.CharField(max_length=200, default='Landcode_LocAfk_ProjAfk_YR_Afk_NightNr_InNightIndex')
    # Landcode_LocatieAfkorting_Project_Afk_Nachtnummer_VolgnummerInNacht

    file = models.FileField(max_length=512, upload_to='tmp')

    original_filename = models.CharField(_('Org. Filename'), max_length=100,
                                         null=True, blank=True)

    sample_frequency = models.IntegerField(_('Samplefrequency (Hz)'),
                                           null=True, blank=True)

    sample_count = models.IntegerField(_('# Samples'),
                                       null=True, blank=True)

    sample_width = models.IntegerField(_('Samplewidth (Bits)'),
                                       null=True, blank=True)

    channel_count = models.IntegerField(_('Number of Channels'),
                                        null=True, blank=True)

    class Meta:
        verbose_name = _("Sound")
        verbose_name_plural = _("Sounds")

    def __str__(self):
        # loc_tz =  pytz.timezone('Europe/Amsterdam') # timezone from Location
        # return str(self.session)+'-['+str(self.recording_date_time.astimezone(loc_tz))+']'
        # fmt = '%Y-%m-%d %H:%M:%S %Z%z'
        return str(self.session)+'-['+str(self.recording_date_time)+']'


    media_dir = "/home/braas/projects/jquery_upload/django-jquery-file-upload/media"
    # session_dir = "/home/braas/projects/jquery_upload/django-jquery-file-upload/media"


    def move_to_session_dir(self):
        # os.makedirs(self.session_dir, exist_ok=True)
        # session_data_dir = os.path.join(str(self.session_id), settings.DATA_DIR)
        relative_processed_data_dir = os.path.join(settings.SESSION_DATA_DIR,
                                                   str(self.session_id),
                                                   settings.DATA_DIR)
        dest_dir = os.path.join(self.media_dir, relative_processed_data_dir)
        os.makedirs(dest_dir, exist_ok=True)
        wav_file_basename = os.path.basename(str(self.file))
        logger.debug('dest_dir: '+dest_dir)
        shutil.move(os.path.join(self.media_dir, str(self.file)),
                    dest_dir)

        self.file.name = os.path.join(relative_processed_data_dir, wav_file_basename)
        logger.debug("File Name:"+self.file.name)
        self.save()


    def create_spectrogram(self):
        logger.debug('create_spectogram: ' + str(self.file))

        img_path_file = (str(self.file)+'.png')  # .lower()

        sox_command = "{0} '{1}' -n spectrogram -m -o '{2}'".format(settings.SOX_CMD,
                                                                    os.path.join(self.media_dir, str(self.file)),
                                                                    os.path.join(self.media_dir, img_path_file))

        logger.debug(sox_command)

        call(sox_command, shell=True)
        return img_path_file

    def create_thumbnail(self):
        size = (256, 256)
        img_path_file = (str(self.file)+'.png') # .lower()
        thumbnail_name = img_path_file.replace(".png", ".thumbnail.png")
        try:
            im = Image.open(os.path.join(self.media_dir, img_path_file))
            im.thumbnail(size)
            im.save(os.path.join(self.media_dir, thumbnail_name))
        except Exception as e:
            error_msg = "Unable to load image : {0} msg: {1}".format(str(self.file),
                                                                     str(e))
            logger.error( error_msg )

class SoundArchive(models.Model):
    session = models.ForeignKey(BatMusicSession, on_delete=models.CASCADE, null=True, blank=True)
    file = models.FileField(_('Archive File'),
                            max_length=512, upload_to='tmp')
    # status
    # logging



    def __str__(self):
        # loc_tz =  pytz.timezone('Europe/Amsterdam') # timezone from Location
        # return str(self.session)+'-['+str(self.recording_date_time.astimezone(loc_tz))+']'
        # fmt = '%Y-%m-%d %H:%M:%S %Z%z'
        return str(self.session)+'-['+str(self.file)+']'

    media_dir = "/home/braas/projects/jquery_upload/django-jquery-file-upload/media"

    def move_to_session_dir(self):
        # os.makedirs(self.session_dir, exist_ok=True)
        # session_data_dir = os.path.join(str(self.session_id), settings.DATA_DIR)
        relative_processed_data_dir = os.path.join(settings.SESSION_DATA_DIR,
                                                   str(self.session_id),
                                                   settings.UNPROCESSED_DATA_DIR)
        dest_dir = os.path.join(self.media_dir, relative_processed_data_dir)
        os.makedirs(dest_dir, exist_ok=True)
        wav_file_basename = os.path.basename(str(self.file))
        logger.debug('dest_dir: '+dest_dir)
        shutil.move(os.path.join(self.media_dir, str(self.file)),
                    dest_dir)

        self.file.name = os.path.join(relative_processed_data_dir, wav_file_basename)
        logger.debug("File Name:"+self.file.name)
        self.save()
