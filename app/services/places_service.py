# places_service.py placeholder
# app/services/places_service.py

"""
Places service layer.

Handles data access and business logic for:
- Nearby hospitals and medical shops
- Filtering by hostel and type
- Creating new places (for admin / seeding)

The routes in places_routes.py can call these functions instead
of directly querying the database everywhere.
"""

from typing import List, Optional

from app.database.db import db
from app.models.place import Place

ALLOWED_HOSTELS = {
    "Boys Hostel 1",
    "Boys Hostel 2",
    "Girls Hostel 1",
    "Girls Hostel 2",
}

ALLOWED_TYPES = {"hospital", "medical_shop"}


def get_places(
    hostel: Optional[str] = None,
    place_type: Optional[str] = None,
) -> List[Place]:
    """
    Fetch places filtered by hostel and / or type.

    Parameters
    ----------
    hostel : str, optional
        One of ALLOWED_HOSTELS. If None, don't filter by hostel.
    place_type : str, optional
        'hospital' or 'medical_shop'. If None, don't filter by type.

    Returns
    -------
    list[Place]
    """
    query = Place.query

    if hostel:
        query = query.filter_by(hostel_tag=hostel)

    if place_type:
        query = query.filter_by(type=place_type)

    return query.order_by(Place.name.asc()).all()


def get_place_by_id(place_id: int) -> Optional[Place]:
    """
    Fetch a single place by its ID.
    """
    return Place.query.get(place_id)


def create_place(
    name: str,
    place_type: str,
    address: str,
    hostel_tag: str,
    phone: Optional[str] = None,
    open_hours: Optional[str] = None,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
) -> Place:
    """
    Create and save a new Place record.

    You can use this from:
    - an admin route
    - a seed script
    - a CLI command

    This function assumes you've already validated the inputs
    (hostel_tag in ALLOWED_HOSTELS, type in ALLOWED_TYPES, etc.)
    """
    place = Place(
        name=name,
        type=place_type,
        address=address,
        hostel_tag=hostel_tag,
        phone=phone,
        open_hours=open_hours,
        latitude=latitude,
        longitude=longitude,
    )

    db.session.add(place)
    db.session.commit()
    return place
