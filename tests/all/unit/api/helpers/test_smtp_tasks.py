import os
import smtplib
import tempfile
import unittest
from unittest.mock import patch

from app.api.helpers.tasks import _build_smtp_message, _send_via_smtp, send_email_task_smtp


def smtp_config(encryption):
    return {'host': 'smtp.example.com', 'port': 587, 'username': 'user', 'password': 'secret',
            'encryption': encryption}


def payload(attachments=None):
    return {'from': 'sender@example.com', 'to': 'rcpt@example.com', 'subject': 'Hello',
            'html': '<p>Hi <b>there</b></p>', 'attachments': attachments}


class TestSmtpTasks(unittest.TestCase):
    def test_message_has_plain_and_html_parts(self):
        message = _build_smtp_message(payload())
        self.assertEqual(message['To'], 'rcpt@example.com')
        self.assertEqual(message['Subject'], 'Hello')
        self.assertIn('Hi there', message.get_body(('plain',)).get_content())
        self.assertIn('<b>there</b>', message.get_body(('html',)).get_content())

    def test_message_attaches_files(self):
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
            f.write(b'%PDF-1.4 test')
        try:
            message = _build_smtp_message(payload([f.name]))
            attachments = list(message.iter_attachments())
            self.assertEqual(len(attachments), 1)
            self.assertEqual(attachments[0].get_content_type(), 'application/pdf')
            self.assertEqual(attachments[0].get_filename(), os.path.basename(f.name))
        finally:
            os.remove(f.name)

    def test_encryption_modes(self):
        message = _build_smtp_message(payload())

        with patch('app.api.helpers.tasks.smtplib.SMTP') as smtp:
            server = smtp.return_value.__enter__.return_value
            _send_via_smtp(smtp_config('required'), message)
            server.starttls.assert_called_once()
            server.login.assert_called_once_with('user', 'secret')
            server.send_message.assert_called_once_with(message)

        with patch('app.api.helpers.tasks.smtplib.SMTP') as smtp:
            server = smtp.return_value.__enter__.return_value
            server.has_extn.return_value = False
            _send_via_smtp(smtp_config('optional'), message)
            server.starttls.assert_not_called()
            server.send_message.assert_called_once()

        with patch('app.api.helpers.tasks.smtplib.SMTP') as smtp:
            server = smtp.return_value.__enter__.return_value
            _send_via_smtp(smtp_config('none'), message)
            server.starttls.assert_not_called()

        with patch('app.api.helpers.tasks.smtplib.SMTP_SSL') as smtp_ssl:
            server = smtp_ssl.return_value.__enter__.return_value
            _send_via_smtp(smtp_config('ssl'), message)
            server.send_message.assert_called_once()

    def test_retries_without_attachments_on_554(self):
        calls = []

        def fake_send(config, message):
            calls.append(len(list(message.iter_attachments())))
            if len(calls) == 1:
                raise smtplib.SMTPResponseException(554, b'rejected')

        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
            f.write(b'%PDF-1.4 test')
        try:
            with patch('app.api.helpers.tasks._send_via_smtp', side_effect=fake_send):
                send_email_task_smtp(payload([f.name]), smtp_config('none'))
        finally:
            os.remove(f.name)
        self.assertEqual(calls, [1, 0])


if __name__ == '__main__':
    unittest.main()
