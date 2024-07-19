from django.conf import settings


def contact_email_addr(request):
    """Creating global context for the support contact email
    to be available in any view without specifically being passed"""
    return {'contact_email': settings.CONTACT_EMAIL}
