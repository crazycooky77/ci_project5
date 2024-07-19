import uuid
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    """Custom user manager model"""
    def create_user(self, password=None, **extra_fields):
        user = self.model(**extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(**extra_fields)

    def get_by_natural_key(self, email):
        return self.get(email__iexact=email)


class User(AbstractUser):
    """Custom user model"""
    username = None
    first_name = None
    last_name = None
    email = models.EmailField(unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email


class Newsletter(models.Model):
    """Model for users subscribed to the newsletter"""
    news_uuid = models.CharField(max_length=32,
                                 unique=True,
                                 blank=False,
                                 null=False,
                                 editable=False)
    news_email = models.EmailField(unique=True)

    def _generate_news_uuid(self):
        """Generate a UUID string to use to unsubscribe from newsletter"""
        return uuid.uuid4().hex.upper()

    def save(self, *args, **kwargs):
        """On save, run the function to generate the UUID"""
        if not self.news_uuid:
            self.news_uuid = self._generate_news_uuid()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.news_email}'
