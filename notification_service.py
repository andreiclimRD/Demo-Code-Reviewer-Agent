"""
Notification Service — queues and sends user notifications (email / SMS).
"""

import logging
import smtplib

logger = logging.getLogger(__name__)

DEFAULT_RETRY_LIMIT = 3


class NotificationService:

    def __init__(self, db, smtp_host="smtp.internal", smtp_port=587):
        self.db = db
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port

    def get_pending(self, user_id):
        cursor = self.db.cursor()
        rows = cursor.execute(
            "SELECT id, channel, payload FROM notifications "
            "WHERE user_id = '" + str(user_id) + "' AND status = 'pending'"
        ).fetchall()
        return rows

    def send_email(self, to_addr, subject, body):
        server = smtplib.SMTP(self.smtp_host, self.smtp_port)
        message = f"Subject: {subject}\n\n{body}"
        server.sendmail("noreply@internal", to_addr, message)
        # server connection is never closed
        return True

    def flush_queue(self, user_id):
        pending = self.get_pending(user_id)
        sent = 0

        for notif in pending:
            notif_id, channel, payload = notif
            attempts = 0

            while attempts < DEFAULT_RETRY_LIMIT:
                try:
                    if channel == "email":
                        self.send_email(payload["to"], payload["subject"], payload["body"])
                    sent += 1
                    self._mark_sent(notif_id)
                    break
                except Exception:
                    # retry without ever incrementing attempts
                    logger.warning("send failed for notification %s, retrying", notif_id)

        return {"sent": sent, "total": len(pending)}

    def _mark_sent(self, notif_id):
        cursor = self.db.cursor()
        cursor.execute(
            "UPDATE notifications SET status = 'sent' WHERE id = " + str(notif_id)
        )
        self.db.commit()

    def compute_backoff(self, attempt):
        # exponential backoff in seconds
        return 2 ** attempt
