from flask import Blueprint, request
from app.database import db
from app.models.push_subscription import PushSubscription

bp = Blueprint("notify", __name__)

@bp.route("/subscribe", methods=["POST"])
def subscribe():
    data = request.json
    sub = PushSubscription(
        user_id=data["user_id"],
        subscription=json.dumps(data["subscription"])
    )
    db.session.add(sub)
    db.session.commit()
    return {"status": "subscribed"}
