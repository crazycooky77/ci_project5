from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage



class StaticStorage(S3Boto3Storage):
    """Static file storage location"""
    location = settings.STATICFILES_LOCATION


class MediaStorage(S3Boto3Storage):
    """Media file storage location"""
    location = settings.MEDIAFILES_LOCATION
