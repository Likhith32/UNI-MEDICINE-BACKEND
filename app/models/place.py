# app/models/place.py

from app.database.db import db


class Place(db.Model):
    """
    Stores information about nearby medical shops and hospitals
    around the university hostels.
    """

    __tablename__ = "places"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # "hospital" or "medical_shop"
    address = db.Column(db.String(255), nullable=False)
    hostel_tag = db.Column(db.String(50), nullable=False)  # e.g., "Boys Hostel 1"

    phone = db.Column(db.String(20), nullable=True)
    open_hours = db.Column(db.String(100), nullable=True)

    # Optional for map display or distance calculations
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)

    def __repr__(self):
        return f"<Place {self.name} ({self.type}) near {self.hostel_tag}>"
