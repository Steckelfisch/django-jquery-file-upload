# -*- coding: utf-8 -*-
import datetime, time
import os, tarfile, zipfile, shutil
import wave
from PIL import Image
from subprocess import call

from django.conf import settings
from django.contrib.sites.models import Site

from .models import BatMusicSession, Sound
import fileupload.batmusic_utils as bm_utils

#from batmusic.mail import send_email_to_user
#from mail.mail_rendering import render_mail

import logging
logger = logging.getLogger(__name__)


def is_archive(name):
    if name.lower().endswith(('.zip', '.tar.gz', '.tgz')):
        return True
    return False


def extract(archive_file, extract_location):
    extract_msg_list = []
    archive_file_basename = os.path.basename(archive_file)  # , errors='replace')
    logger.debug("extract: {0}".format(archive_file_basename))
    extract_msg_list.append(u"extract: Process ")
    try:
        extract_msg_list.append(archive_file_basename)
    except UnicodeDecodeError as ude:
        extract_msg_list.append(ude)
        return extract_msg_list

    if archive_file.lower().endswith(('.tar.gz', '.tgz')):
        with tarfile.open(archive_file) as tar_archive:
            try:
                tar_archive_files = tar_archive.getmembers()
                for tar_archive_file in tar_archive_files:
                    # logger.info(u"process " + str(tar_archive_file.name, errors='replace'))
                    if tar_archive_file.isfile():
                        tar_archive.extract(tar_archive_file, extract_location)
                        extracted_file = os.path.join(extract_location, tar_archive_file.name)
                        try:
                            os.chmod(extracted_file, 0o644)
                        except Exception as e:
                            msg = u'Error chmod "{0}" {1}'.format(extracted_file, str(e))
                            extract_msg_list.append(msg)
            except Exception as e:
                msg = u'Error extracting "{0}" {1}'.format(archive_file_basename, str(e))
                extract_msg_list.append(msg)
        return extract_msg_list

    elif archive_file.lower().endswith(('.zip',)):
        with zipfile.ZipFile(archive_file) as zip_archive:
            for zip_info in zip_archive.infolist():
                zip_archive.extract(zip_info, extract_location)
                date_time = time.mktime(zip_info.date_time + (0, 0, -1))
                os.utime(zip_info.filename, (date_time, date_time))
        return extract_msg_list
    else:
        extract_msg_list.append('Unrecognized extention: {0}'.format(archive_file))

    return extract_msg_list


def dict_to_sound_attribute(data_dict, allowed_attribute_name_id_dict,
                            sound_item, row_count=0):
    msg_list = []
    for field_name, field_value in data_dict.items():
        sound_attribute_id = allowed_attribute_name_id_dict.get(field_name.lower())
        #if sound_attribute_id:
        #     new_sound_attribute = SoundAttribute.objects.create(sound=sound_item,
        #                                                 attribute_id=sound_attribute_id,
        #                                                 att_index = row_count,
        #                                                 value=field_value)
        #else:
        #     msg_list.append('unsupported attribute: "{0}"'.format(field_name))
    return msg_list


def save_session_upload_log(bm_session, session_log):
    bm_session_data_dir = bm_session.get_data_dir()
    session_logfile = os.path.join(bm_session_data_dir, 'upload.log')
    with open(session_logfile, 'a') as f:
        f.write("\n".join(session_log))
        f.write("\n")


def process_uploaded_session_data(bm_session_id, **kwargs):
    logger.debug('process_uploaded_session_data '+str(bm_session_id))
    bm_session = BatMusicSession.objects.get(pk=bm_session_id)
    # bm_session_data_dir = bm_session.get_data_dir()

    session_log = []

    # Todo: take from or merge with session.get_data_dirs()
    session_data_dirs = bm_session.get_data_dirs()
    unprocessed_data_dir = session_data_dirs.get('unprocessed_data_dir')
    extracted_data_dir = session_data_dirs.get('extracted_data_dir')
    backup_data_dir = session_data_dirs.get('backup_data_dir')

    # first extract archive files
    # and move archive files to BACKUPD_DATA_DIR
    logger.debug(u"unprocessed_data_dir: {0}".format(unprocessed_data_dir))
    filelist = os.listdir(unprocessed_data_dir)
    filelist = filter(lambda x: not os.path.isdir(x), filelist)
    archive_filelist = list(filter(lambda x: is_archive(x), filelist))
    session_log.append(u"Archive list: {0}".format(archive_filelist))
    for archive_file in archive_filelist:
        logger.debug(u"extract file: {0}".format(archive_file))
        path_archive_file = os.path.join(unprocessed_data_dir, archive_file)
        session_log += extract(path_archive_file, extracted_data_dir)
        # Todo: what if this archive file is uploaded before
        shutil.move(path_archive_file,
                    os.path.join(backup_data_dir, archive_file))

    # update logfile
    logger.debug("session_log extraction: {0}".format(session_log))
    bm_session.save_upload_log(session_log)
    session_log = []

    # the variables UNPROCESSED_DATA_DIR and EXTACTED_DATA_DIR now have
    # datafiles, (wav files and additional info files)
    # all compressed files are moved to BACKUP_DATA_DIR

    session_log += _proces_unprocessed_data_dir(unprocessed_data_dir, extracted_data=False, bm_session=bm_session)
    session_log += _proces_unprocessed_data_dir(extracted_data_dir, extracted_data=True, bm_session=bm_session)

    # update logfile
    logger.debug("session_log processing : {0}".format(session_log))
    bm_session.save_upload_log(session_log)
    session_log = []

    # TODO: save BatMusicSession met localized UTC.
    # time_zone = pytz.timezone('Europe/Amsterdam') # bm_session.location.timezone
    # bm_session.last_upload_trigger_date_time = time_zone.localize( datetime.datetime.utcnow())
    bm_session.last_upload_trigger_date_time = datetime.datetime.utcnow()
    bm_session.save()
    session_log.append('Updated session record')

    # update logfile
    logger.debug("session_log session: {0}".format(session_log))
    bm_session.save_upload_log(session_log)
    # session_log = []

    # mail to user
    mail_template_name = 'process_uploaded_session'
    from_name_email = ["BatMusicServer", settings.EMAIL_HOST_USER]
    mail_context = {}
    try:
        mail_context ={
            'bm_session': bm_session,
            'user': bm_session.user,
            'user_name': bm_session.user.get_full_name() if bm_session.user.get_full_name() else bm_session.user,
            'site': Site.objects.get_current()
        }
        #mail_render_result = render_mail(mail_template_name, mail_context=mail_context)

        to_name_email = [bm_session.user.get_full_name() ,bm_session.user.email]
        #send_email_to_user(from_email=from_name_email[1],
        #                   to_email=to_name_email[1],
        #                   subject=mail_render_result['subject'],
        #                   html_content=mail_render_result['html_content'],
        #                   text_content=mail_render_result['text_content'])
    except Exception as e:
        error_mail_subject = "Batmusic Template error for template {0}.".format(mail_template_name)
        error_mail_content = "Error: {0} \n Name: {1} \n Context: {2}".format(str(e),
                                                                              mail_template_name,
                                                                              mail_context.keys())
        #for nameAdres in settings.MANAGERS:
        #    send_email_to_user(from_email=from_name_email[1],
        #                       to_email=nameAdres[1],
        #                      subject=error_mail_subject,
        #                       html_content="<html><body>{0}</body></html>".format(error_mail_content.replace('\n',
        #                                                                                                      '<br/>')),
        #                      text_content=error_mail_content)


def _get_record_datetime_and_filename(wav_file, bm_session, from_extracted_src, try_count=0):
    '''
     get record_datetime from filename or the files mtime
     if taken from mtime, rename the file to batmusic standard

     return record_datetime, filename, old_filename

     throws Exception if no date and time could be inferred
    '''
    sound_file_name = os.path.basename(wav_file)
    org_filename = sound_file_name
    filename = sound_file_name
    logger.info("org_filename: "+org_filename)
    if bm_session.recorder:
        recorder = bm_session.recorder
        logger.debug("_get_record_datetime_and_filename: use recorder setting: {0}".format(
                                                                          str(recorder.get_datetime_format_display())))
        record_datetime = bm_session.recorder.get_date_time_from_filename(sound_file_name)
    else:
        logger.info("_get_record_datetime_and_filename: use 'no recorder setting'")
        record_datetime = bm_utils.get_date_time_from_filename(sound_file_name)
    if not record_datetime:
        if from_extracted_src:
            record_datetime = bm_utils.get_date_time_from_file(wav_file)
        else:  # date and time cannot be obtained
            raise Exception(u'date and time cannot be obtained from "'+sound_file_name+'"')
    if not bm_session.daylight_saving_correction:
        logger.debug("Batmusic has to apply DST correction")
        dst_correction = bm_utils.get_dst_correction(bm_session.location,
                                                     record_datetime,
                                                     bm_session.recordingtime_in_dst)
        if dst_correction != 0:
            # logger.info(u'toepassen DST correctie hours '+str(dst_correction))
            record_datetime += datetime.timedelta(hours=dst_correction)

    filename = bm_utils.rename_to_batmusic_standard(filename, bm_session.location, record_datetime, try_count)
    return record_datetime, filename, org_filename

'''
def _create_bm_filename(filename, data_dirs) :
    sounditem_audiofile = os.path.join(data_dirs.get('processed_data_dir'), filename)
    relative_sounditem_audiofile = os.path.join(data_dirs.get('relative_processed_data_dir'), filename)
    # check for existence of org_filename in this sessions wav-file set
    if os.path.isfile(sounditem_audiofile):
        # if it exists, it is uploaded a second time
        #   create a message in the logfile
        #   continue with next wav file (return None, None
        # if it does not exist, try alternative versions of the bm-generated filename
        try:
            SoundItem.objects.get(session=bm_session,
                                  original_filename=org_filename)
            session_log.append("soundfile '" + org_filename + "' is already loaded for this session. Remove.")
            # todo: move from unprocessed to .....
            os.remove(wav_file)
            return None, None
        except SoundItem.DoesNotExist as dne:
            session_log.append(
                "soundfile '" + org_filename + "' has identical timed files in this session. Try alternatives.")
            pass
        except Exception as e:
            session_log.append(
                "soundfile '" + org_filename + "' has other problems in this session. Do not try alternatives. Remove.")
            # todo: move from unprocessed to .....
            os.remove(wav_file)
            return None, None

        try_count = 0
        while os.path.isfile(sounditem_audiofile):
            session_log.append("produce filename alternatives " + str(try_count))
            try_count += 1
            # try - catch not needed here, succeded once already
            record_datetime, filename, org_filename = _get_record_datetime_and_filename(wav_file,
                                                                                        bm_session,
                                                                                        extracted_data,
                                                                                        try_count)
            sounditem_audiofile = os.path.join(data_dirs.get('processed_data_dir'), filename)
            relative_sounditem_audiofile = os.path.join(data_dirs.get('relative_processed_data_dir'), filename)
    return sounditem_audiofile, relative_sounditem_audiofile
'''


def _proces_unprocessed_data_dir(unprocessed_data_dir, extracted_data, bm_session):
    '''
    :param unprocessed_data_dir:
    :param extracted_data: data is uploaded in tgz, zip, (...) file. Date-time is preserved on server
    :param bm_session:
    :return:
    '''
    session_log = []
    data_dirs = bm_session.get_data_dirs()

    wav_filelist = [os.path.join(dirpath, f) for dirpath, dirnames, filenames in os.walk(unprocessed_data_dir)
                    for f in filenames if (os.path.splitext(f)[1]).lower() == '.wav']
    # wav_filelist = list(wav_filelist)
    # progress_count = 0
    logger.debug("wav_filelist: "+str(wav_filelist))
    for wav_file in wav_filelist:
        session_log.append('==============================================')
        wav_file_basename = os.path.basename(wav_file)
        session_log.append('process: '+wav_file)
        session_log.append('process: '+wav_file_basename)
        record_datetime, filename, org_filename = None, None, None
        # '''
        try:
            record_datetime, filename, org_filename = _get_record_datetime_and_filename(wav_file,
                                                                                        bm_session,
                                                                                        extracted_data)

            # sounditem's recording time should lie between start and enddate of session
            logger.info("? "+str(bm_session.start_date_time)+"<"+str(record_datetime)+"<"+str(bm_session.end_date_time))
            if record_datetime.date() < bm_session.start_date_time.date() or \
               bm_session.end_date_time.date() < record_datetime.date():
                exeption_msg = u"{0} outside session start_date({1})/end_date({2})".format(record_datetime,
                                                                                           bm_session.start_date_time.date(),
                                                                                           bm_session.end_date_time.date())
                raise Exception(exeption_msg)
        # '''
        except Exception as e:
            logger.debug("proces_unprocessed_data_dir: "+str(e))
            error_msg = u"\nError extracting date-time from soundfile '{0}': {1}".format(wav_file_basename, e)
            session_log.append(error_msg)
            try:
                # logger.debug("wav_file:"+wav_file)
                shutil.move(wav_file, data_dirs.get('rejected_data_dir'))
            except Exception as shutil_ex:
                logger.error("proces_unprocessed_data_dir shutil.move: "+str(shutil_ex))
            # shutil.move(wav_file, data_dirs.get('rejected_data_dir'))
            # os.remove(wav_file)
            continue

        sounditem_audiofile = os.path.join(data_dirs.get('processed_data_dir'), filename)
        relative_sounditem_audiofile = os.path.join(data_dirs.get('relative_processed_data_dir'), filename)
        # check for existence of org_filename in this sessions wav-file set
        if os.path.isfile(sounditem_audiofile):
            # if it exists, it is uploaded a second time
            #   create a message in the logfile
            #   continue with next wav file
            # if it does not exist, try alternative versions of the bm-generated filename
            try:
                Sound.objects.get(session=bm_session,
                                      original_filename=org_filename)
                error_msg = "soundfile '{0}' is already loaded for this session. Remove.".format(org_filename)
                session_log.append(error_msg)
                # todo: move from unprocessed to .....
                os.remove(wav_file)
                continue
            except Sound.DoesNotExist as dne:
                error_msg = "soundfile '{0}' has identical timed files in this session. Try alternatives.".format(org_filename)
                session_log.append(error_msg)
                pass
            except Exception as e:
                error_msg = "soundfile '{0}' has other problems in this session ({1}). Do not try alternatives. Remove."
                error_msg.format(org_filename, str(e))
                session_log.append(error_msg)
                # shutil.move(wav_file, os.path.join(data_dirs.get('rejected_data_dir'), filename))
                shutil.move(wav_file, data_dirs.get('rejected_data_dir'))
                # os.remove(wav_file)
                continue

            try_count = 0
            while os.path.isfile(sounditem_audiofile):
                session_log.append(u"produce filename alternatives " + str(try_count))
                try_count += 1
                # try - catch not needed here, succeded once already
                record_datetime, filename, org_filename = _get_record_datetime_and_filename(wav_file,
                                                                                            bm_session,
                                                                                            extracted_data,
                                                                                            try_count)
                sounditem_audiofile = os.path.join(data_dirs.get('processed_data_dir'), filename)
                relative_sounditem_audiofile = os.path.join(data_dirs.get('relative_processed_data_dir'), filename)

        # move (and possible rename) wav-file from UNPROCESSED_DATA_DIR to DATA_DIR
        shutil.move(wav_file, sounditem_audiofile)

        #========================================================
        # create_sounditem_from_wav_file(wav_file, old_filename=None)
        # fetch .wav characteristics
        # and create SoundItem
        sample_frequency = None
        sample_count = None
        sample_width = None
        channel_count = None
        try:
            # see https://docs.python.org/2/library/wave.html
            # todo: use with wave.open(sounditem_audiofile) as wav_fh
            wav_fh = wave.open(sounditem_audiofile)
            wav_params = wav_fh.getparams()

            channel_count = wav_params[0]
            sample_width = 8*wav_params[1]  # bytes to bits
            sample_frequency = wav_params[2]
            sample_count = wav_params[3]
        except Exception as e:
            session_log.append('Error fetching .wav info from {0} : {1}'.format(sounditem_audiofile,
                                                                                str(e)))
            # TODO: move file to error-dir.
            # os.remove(sounditem_audiofile)
            continue
        finally:
            wav_fh.close()

        new_sound_item = Sound.objects.create(session=bm_session,
                                                  file=relative_sounditem_audiofile,
                                                  recording_date_time=record_datetime,
                                                  sample_frequency=sample_frequency,
                                                  sample_count=sample_count,
                                                  sample_width=sample_width,
                                                  channel_count=channel_count,
                                                  original_filename=org_filename)
        # create spectrogram images
        try:
            session_log.append('Create spectrogram for '+str(sounditem_audiofile))
            specrogram_file = _create_spectrogram(sounditem_audiofile)
            _create_thumbnail(specrogram_file)
            session_log.append('Created spectrogram.')
        except Exception as e:
            error_msg = 'Error generating .png or .thumbnail.png from {0} : {1}'.format(new_sound_item.audio_file,
                                                                                        str(e))
            session_log.append(error_msg)

    return session_log


def _create_spectrogram(fd_wav_file):
    logger.debug('create_spectogram: ' + str(fd_wav_file))

    img_path_file = (str(fd_wav_file)+'.png').lower()

    sox_command = "{0} '{1}'  -n spectrogram -m -o '{2}'".format(settings.SOX_CMD, fd_wav_file, img_path_file)

    logger.info(sox_command)

    call(sox_command, shell=True)
    return img_path_file


def _create_thumbnail(img_file):
    size = (256, 256)
    thumbnail_name = img_file.lower().replace(".wav", ".wav.thumbnail")
    try:
        im = Image.open(img_file)
        im.thumbnail(size)
        im.save(thumbnail_name)
    except Exception as e:
        error_msg = "Unable to load image : {0} msg: {1}".format(img_file,
                                                                 str(e))
        logger.error( error_msg )
