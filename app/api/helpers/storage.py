import os
from base64 import b64encode
from shutil import copyfile, rmtree

import boto3
import magic
from botocore.config import Config
from flask import current_app as app, request
from flask_scrypt import generate_password_hash
from urllib.parse import urlparse
from werkzeug.utils import secure_filename

from app.settings import get_settings

SCHEMES = {80: 'http', 443: 'https'}

#################
# STORAGE SCHEMA
#################

UPLOAD_PATHS = {
    'sessions': {
        'video': 'events/{event_id}/sessions/{id}/video',
        'audio': 'events/{event_id}/audios/{id}/audio',
        'slides': 'events/{event_id}/slides/{id}/slides'
    },
    'speakers': {
        'photo': 'events/{event_id}/speakers/{id}/photo',
        'thumbnail': 'events/{event_id}/speakers/{id}/thumbnail',
        'small': 'events/{event_id}/speakers/{id}/small',
        'icon': 'events/{event_id}/speakers/{id}/icon'
    },
    'event': {
        'logo': 'events/{event_id}/logo',
        'original': 'events/{identifier}/original',
        'thumbnail': 'events/{identifier}/thumbnail',
        'large': 'events/{identifier}/large',
        'icon': 'events/{identifier}/icon'
    },
    'sponsors': {
        'logo': 'events/{event_id}/sponsors/{id}/logo'
    },
    'user': {
        'avatar': 'users/{user_id}/avatar',
        'thumbnail': 'users/{identifier}/thumbnail',
        'original': 'users/{identifier}/original',
        'small': 'users/{identifier}/small',
        'icon': 'users/{identifier}/icon'
    },
    'temp': {
        'event': 'events/temp/{uuid}',
        'image': 'temp/images/{uuid}'
    },
    'exports': {
        'zip': 'exports/{event_id}/zip',
        'pentabarf': 'exports/{event_id}/pentabarf',
        'ical': 'exports/{event_id}/ical',
        'xcal': 'exports/{event_id}/xcal',
        'csv': 'exports/{event_id}/csv/{identifier}',
        'pdf': 'exports/{event_id}/pdf/{identifier}'
    },
    'exports-temp': {
        'zip': 'exports/{event_id}/temp/zip',
        'pentabarf': 'exports/{event_id}/temp/pentabarf',
        'ical': 'exports/{event_id}/temp/ical',
        'xcal': 'exports/{event_id}/temp/xcal',
        'csv': 'exports/{event_id}/csv/{identifier}',
        'pdf': 'exports/{event_id}/pdf/{identifier}'
    },
    'custom-placeholders': {
        'original': 'custom-placeholders/{identifier}/original',
        'thumbnail': 'custom-placeholders/{identifier}/thumbnail',
        'large': 'custom-placeholders/{identifier}/large',
        'icon': 'custom-placeholders/{identifier}/icon'
    },
    'event_topic': {
        'system_image': 'event_topic/{event_topic_id}/system_image'
    },
    'pdf': {
        'ticket_attendee': 'attendees/tickets/pdf/{identifier}',
        'order': 'orders/invoices/pdf/{identifier}',
        'tickets_all': 'orders/tickets/pdf/{identifier}',
        'event_invoice': 'events/organizer/invoices/pdf/{identifier}'
    }
}


################
# HELPER CLASSES
################

class UploadedFile(object):
    """
    Helper for a disk-file to replicate request.files[ITEM] class
    """

    def __init__(self, file_path, filename):
        self.file_path = file_path
        self.filename = filename
        self.file = open(file_path)

    def save(self, new_path):
        copyfile(self.file_path, new_path)

    def read(self):
        return self.file.read()

    def __exit__(self, *args, **kwargs):
        self.file.close()


class UploadedMemory(object):
    """
    Helper for a memory file to replicate request.files[ITEM] class
    """

    def __init__(self, data, filename):
        self.data = data
        self.filename = filename

    def read(self):
        return self.data

    def save(self, path):
        f = open(path, 'w')
        f.write(str(self.data, 'utf-8'))
        f.close()


#########
# MAIN
#########

def upload(uploaded_file, key, upload_dir='static/media/', **kwargs):
    """
    Upload handler
    """
    # refresh settings
    aws_bucket_name = get_settings()['aws_bucket_name']
    aws_key = get_settings()['aws_key']
    aws_secret = get_settings()['aws_secret']
    aws_region = get_settings()['aws_region']

    gs_bucket_name = get_settings()['gs_bucket_name']
    gs_key = get_settings()['gs_key']
    gs_secret = get_settings()['gs_secret']

    storage_place = get_settings()['storage_place']

    # upload
    if aws_bucket_name and aws_key and aws_secret and storage_place == 's3':
        return upload_to_aws(aws_bucket_name, aws_region, aws_key, aws_secret, uploaded_file, key, **kwargs)
    elif gs_bucket_name and gs_key and gs_secret and storage_place == 'gs':
        return upload_to_gs(gs_bucket_name, gs_key, gs_secret, uploaded_file, key, **kwargs)
    else:
        return upload_local(uploaded_file, key, upload_dir, **kwargs)


def upload_local(uploaded_file, key, upload_dir='static/media/', **kwargs):
    """
    Uploads file locally. Base dir - static/media/
    """
    filename = secure_filename(uploaded_file.filename)
    file_relative_path = upload_dir + key + '/' + generate_hash(key) + '/' + filename
    file_path = app.config['BASE_DIR'] + '/' + file_relative_path
    dir_path = file_path.rsplit('/', 1)[0]
    # delete current
    try:
        rmtree(dir_path)
    except OSError:
        pass
    # create dirs
    if not os.path.isdir(dir_path):
        os.makedirs(dir_path)
    uploaded_file.save(file_path)
    file_relative_path = '/' + file_relative_path
    if get_settings()['static_domain']:
        return get_settings()['static_domain'] + \
               file_relative_path

    return create_url(request.url, file_relative_path)


def create_url(request_url, file_relative_path):
    """Generates the URL of an uploaded file."""
    url = urlparse(request_url)

    # No need to specify scheme-corresponding port
    port = url.port
    if port and url.scheme == SCHEMES.get(url.port, None):
        port = None

    return '{scheme}://{hostname}:{port}{file_relative_path}'.format(
        scheme=url.scheme, hostname=url.hostname, port=port,
        file_relative_path=file_relative_path).replace(':None', '')


def _upload_with_boto3(client, bucket_name, file, key, acl):
    """
    Uploads `file` below `key` in the bucket through an S3 compatible client.
    Returns the object key, or False if the upload failed.
    """
    filename = secure_filename(file.filename)
    key_dir = key + '/' + generate_hash(key) + '/'
    object_key = key_dir + filename

    # delete old data
    listing = client.list_objects_v2(Bucket=bucket_name, Prefix=key_dir)
    for item in listing.get('Contents', []):
        client.delete_object(Bucket=bucket_name, Key=item['Key'])

    file_data = file.read()
    file_mime = magic.from_buffer(file_data, mime=True)
    response = client.put_object(
        Bucket=bucket_name,
        Key=object_key,
        Body=file_data,
        ContentDisposition='attachment; filename=%s' % filename,
        ContentType='%s' % file_mime,
        ACL=acl,
    )
    if response.get('ResponseMetadata', {}).get('HTTPStatusCode') == 200:
        return object_key
    return False


def upload_to_aws(bucket_name, aws_region, aws_key, aws_secret, file, key, acl='public-read'):
    """
    Uploads to AWS at key
    http://{bucket}.s3.amazonaws.com/{key}
    """
    options = {}
    if '.' in bucket_name:
        # bucket names containing dots do not work with virtual hosted style TLS
        options['config'] = Config(s3={'addressing_style': 'path'})
    if aws_region:
        options['region_name'] = aws_region

    client = boto3.client('s3', aws_access_key_id=aws_key, aws_secret_access_key=aws_secret, **options)
    object_key = _upload_with_boto3(client, bucket_name, file, key, acl)
    if object_key:
        return 'https://%s.s3.amazonaws.com/%s' % (bucket_name, object_key)
    return False


def upload_to_gs(bucket_name, client_id, client_secret, file, key, acl='public-read'):
    # Google Cloud Storage is reachable through its S3 compatible (HMAC key) endpoint
    client = boto3.client(
        's3',
        endpoint_url='https://storage.googleapis.com',
        aws_access_key_id=client_id,
        aws_secret_access_key=client_secret,
        config=Config(s3={'addressing_style': 'path'}),
    )
    object_key = _upload_with_boto3(client, bucket_name, file, key, acl)
    if object_key:
        return 'https://storage.googleapis.com/%s/%s' % (bucket_name, object_key)
    return False


# ########
# HELPERS
# ########


def generate_hash(key):
    """
    Generate hash for key
    """
    phash = generate_password_hash(key, get_settings()['secret'])
    return str(b64encode(phash), 'utf-8')[:10]  # limit len to 10, is sufficient
