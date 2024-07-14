from django.conf import settings


def contact_email_addr(request):
    return {'contact_email': settings.CONTACT_EMAIL}
