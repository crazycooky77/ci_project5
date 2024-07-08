from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import render
from django.template.loader import render_to_string


def handler404(request, exception):
    return render(request, "404.html", status=404)


def handler500(request, exception):
    def _send_admin_500_email(e):
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

    _send_admin_500_email(exception)
    return render(request, "500.html", status=500)
