import sys
from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import render
from django.template.loader import render_to_string


def error_handler_emails(request, err_no):
    """Custom handler/view"""
    type_, value, traceback = sys.exc_info()
    url = request.get_full_path()
    user = request.user

    def _send_admin_email(loc, origin, *args):
        """Function to send an email to admin
        for any server errors, so they can be investigated"""
        if args:
            e = []
            for arg in args:
                e.append(arg)
        else:
            e = None
        admin_email = settings.CONTACT_EMAIL
        subject = render_to_string(
            f'error_emails/admin-{err_no}-subject.txt')
        body = render_to_string(
            f'error_emails/admin-{err_no}-body.txt',
            {'e': e,
             'loc': loc,
             'origin': origin})

        send_mail(
            subject,
            body,
            settings.DEFAULT_FROM_EMAIL,
            [admin_email])

    _send_admin_email(url, user, type_, value, traceback)


def csrf_failure(request, reason=""):
    """Custom csrf failure handler/view"""
    error_handler_emails(request, 'csrf')
    return render(request, '403_csrf.html', status=403)


def handler404(request, exception):
    """Custom 404 handler/view"""
    return render(request, '404.html', status=404)


def handler500(request):
    """Custom 500 handler/view"""
    error_handler_emails(request, '500')
    return render(request, '500.html', status=500)
