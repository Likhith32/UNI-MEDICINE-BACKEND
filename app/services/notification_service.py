import json
from pywebpush import webpush
from flask import current_app
from app.database.db import db
from app.models.push_subscription import PushSubscription

def send_push_to_user(user_id, title, body):
    subs = PushSubscription.query.filter_by(user_id=user_id).all()

    for sub in subs:
        webpush(
            subscription_info=json.loads(sub.subscription),
            data=json.dumps({
                "title": title,
                "body": body
            }),
            vapid_private_key=current_app.config["VAPID_PRIVATE_KEY"],
            vapid_claims={"sub": "mailto:admin@yourapp.com"}
        )
