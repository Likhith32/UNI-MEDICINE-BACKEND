from app.database.db import db

class PushSubscription(db.Model):
    __tablename__ = "push_subscriptions"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),   # ✅ FIX 1
        nullable=False,
        index=True
    )

    subscription = db.Column(
        db.Text,
        nullable=False
    )

    # ✅ FIX 2
    user = db.relationship(
        "User",
        back_populates="push_subscriptions"
    )
