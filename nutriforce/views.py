import sys

from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import render
from django.template.loader import render_to_string


def handler404(request, exception):
    return render(request, "404.html", status=404)


def handler500(request):
    type_, value, traceback = sys.exc_info()

    def _send_admin_500_email(*args):
        if args:
            e = []
            for arg in args:
                e.append(arg)
        else:
            e = None
        admin_email = settings.CONTACT_EMAIL
        subject = render_to_string(
            'error_emails/admin_500_subject.txt')
        body = render_to_string(
            'error_emails/admin_500_body.txt',
            {'e': e})

        send_mail(
            subject,
            body,
            settings.DEFAULT_FROM_EMAIL,
            [admin_email])

    _send_admin_500_email(type_, value, traceback)
    return render(request, "500.html", status=500)
