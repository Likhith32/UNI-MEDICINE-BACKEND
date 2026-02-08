from app import create_app
from app.database.db import db
from app.models.place import Place


DEFAULT_HOSTEL = "Boys Hostel 1"

ALLOWED_HOSTELS = {
    "Boys Hostel 1",
    "Boys Hostel 2",
    "Girls Hostel 1",
    "Girls Hostel 2",
}


def normalize_type(value: str) -> str:
    v = value.strip().lower()

    if v in {"hospital", "hospitals"}:
        return "hospital"

    if v in {
        "medical_shop",
        "medical shop",
        "medicalshop",
        "pharmacy",
        "pharmacies",
    }:
        return "medical_shop"

    raise ValueError(f"Invalid place type: {value}")


def normalize_hostel(value: str) -> str:
    value = value.strip()
    if value not in ALLOWED_HOSTELS:
        raise ValueError(f"Invalid hostel_tag: {value}")
    return value


def normalize_str(value):
    return value.strip() if isinstance(value, str) else value



RAW_PLACES = [
    {
        "name": "Venkata Padma Hospital",
        "type": "HOSPITAL",
        "address": "Three Lamps Junction, AG Road, Vizianagaram",
        "hostel_tag": DEFAULT_HOSTEL,
        "phone": "+91 90002 67654",
        "open_hours": "24 Hours",
        "latitude": 18.1088126,
        "longitude": 83.4173236,
    },
    {
        "name": "Queens NRI Hospital",
        "type": "HOSPITAL",
        "address": "Opp SBI Main Branch, Near NCS Theatre, Vizianagaram",
        "hostel_tag": DEFAULT_HOSTEL,
        "phone": "08922 251777",
        "open_hours": "24 Hours",
        "latitude": 18.1160657,
        "longitude": 83.4029738,
    },
    {
        "name": "Mahendra Hospitals",
        "type": "HOSPITAL",
        "address": "RCM Church Road, Cantonment, Vizianagaram",
        "hostel_tag": DEFAULT_HOSTEL,
        "phone": "08922 222555",
        "open_hours": "24 Hours",
        "latitude": 18.1159,
        "longitude": 83.4025,
    },
    {
        "name": "Maharaja District Hospital",
        "type": "HOSPITAL",
        "address": "RCM Church Road, Vizianagaram",
        "hostel_tag": DEFAULT_HOSTEL,
        "phone": "08922 228800",
        "open_hours": "24 Hours (Govt.)",
        "latitude": 18.1409,
        "longitude": 83.2987,
    },
    {
        "name": "Venkata Rama Hospital",
        "type": "HOSPITAL",
        "address": "Opp RTC Complex, Vizianagaram",
        "hostel_tag": DEFAULT_HOSTEL,
        "phone": "08922 273777",
        "open_hours": "24 Hours",
        "latitude": 18.1185,
        "longitude": 83.4045,
    },
    {
        "name": "Pushpagiri Eye Hospital",
        "type": "HOSPITAL",
        "address": "Near TTD Kalyana Mandapam, Alaknagar, Vizianagaram",
        "hostel_tag": DEFAULT_HOSTEL,
        "phone": "08922 270070",
        "open_hours": "9 AM - 8 PM",
        "latitude": 18.115508,
        "longitude": 83.411954,
    },
    {
        "name": "Vamsi Children Hospital",
        "type": "HOSPITAL",
        "address": "Vizianagaram",
        "hostel_tag": DEFAULT_HOSTEL,
        "phone": "9440193885",
        "open_hours": "24 Hours (Pediatrics)",
        "latitude": 18.1170,
        "longitude": 83.3990,
    },
    {
        "name": "PG Star Hospital",
        "type": "HOSPITAL",
        "address": "Rangala Street, Vizianagaram",
        "hostel_tag": DEFAULT_HOSTEL,
        "phone": "08922 272727",
        "open_hours": "24 Hours",
        "latitude": 18.1115,
        "longitude": 83.4060,
    },
    {
        "name": "A J Global Health Care Hospital",
        "type": "HOSPITAL",
        "address": "100 Feet Ring Road, Vinayaka Nagar, Vizianagaram",
        "hostel_tag": DEFAULT_HOSTEL,
        "phone": "08922 299911",
        "open_hours": "24 Hours",
        "latitude": 18.1300,
        "longitude": 83.3880,
    },
    {
        "name": "MIMS Hospital, Nellimarla",
        "type": "HOSPITAL",
        "address": "Nellimarla, Vizianagaram",
        "hostel_tag": DEFAULT_HOSTEL,
        "phone": "08922 240777",
        "open_hours": "24 Hours",
        "latitude": 18.146964,
        "longitude": 83.445320,
    },

    {
        "name": "Apollo Pharmacy - MG Road",
        "type": "MEDICAL_SHOP",
        "address": "MG Road, Vizianagaram",
        "hostel_tag": DEFAULT_HOSTEL,
        "phone": "08922 279999",
        "open_hours": "24 Hours",
        "latitude": 18.1244906,
        "longitude": 83.3874123,
    },
    {
        "name": "MedPlus Pharmacy - Vizianagaram",
        "type": "MEDICAL_SHOP",
        "address": "Market Area, Vizianagaram",
        "hostel_tag": DEFAULT_HOSTEL,
        "phone": "08922 278888",
        "open_hours": "8 AM - 10 PM",
        "latitude": 18.1017172,
        "longitude": 83.3927211,
    },
    {
        "name": "Datta Pharmacy",
        "type": "MEDICAL_SHOP",
        "address": "Kothagraharam Market, Vizianagaram",
        "hostel_tag": DEFAULT_HOSTEL,
        "phone": "08922 270123",
        "open_hours": "9 AM - 10 PM",
        "latitude": 18.1105,
        "longitude": 83.4008,
    },
    {
        "name": "MS Satyanarayana Pharmacy",
        "type": "MEDICAL_SHOP",
        "address": "Near SKP Temple, Vizianagaram",
        "hostel_tag": DEFAULT_HOSTEL,
        "phone": "08922 271234",
        "open_hours": "9 AM - 10 PM",
        "latitude": 18.1110,
        "longitude": 83.4020,
    },
    {
        "name": "Pradhan Mantri Janaushadhi Kendra",
        "type": "MEDICAL_SHOP",
        "address": "Bodduvari Junction, Vizianagaram",
        "hostel_tag": DEFAULT_HOSTEL,
        "phone": "08922 276543",
        "open_hours": "9 AM - 9 PM",
        "latitude": 18.1150,
        "longitude": 83.3965,
    },
]



def seed_places(clear_existing=True):
    if clear_existing:
        print("⚠️ Clearing existing places...")
        Place.query.delete()
        db.session.commit()

    created = 0

    for raw in RAW_PLACES:
        try:
            place = Place(
                name=normalize_str(raw["name"]),
                type=normalize_type(raw["type"]),
                address=normalize_str(raw["address"]),
                hostel_tag=normalize_hostel(raw["hostel_tag"]),
                phone=normalize_str(raw.get("phone")),
                open_hours=normalize_str(raw.get("open_hours")),
                latitude=raw.get("latitude"),
                longitude=raw.get("longitude"),
            )
            db.session.add(place)
            created += 1
        except Exception as e:
            print(f"❌ Skipped {raw.get('name')} → {e}")

    db.session.commit()
    print(f"✅ Seed completed: {created} places inserted")



if __name__ == "__main__":
    app = create_app()              # ✅ create Flask app
    with app.app_context():         # ✅ push app context
        seed_places(clear_existing=True)
DEFAULT_HOSTEL = "Boys Hostel 1"


def get_seed_places():
    """
    Returns a list of dicts to seed into the Place table.

    type:
      - "hospital"
      - "medical_shop"
    """
    return [
        # ---------- HOSPITALS (10) ---------- #
        {
            "name": "Venkata Padma Hospital",
            "type": "hospital",
            "address": "Three Lamps Junction, AG Road, Vizianagaram",
            "hostel_tag": DEFAULT_HOSTEL,
            "phone": "+91 90002 67654",
            "open_hours": "24 Hours",
            # Verified from insurer/network listing (Three Lamps Jn)
            "latitude": 18.1088126,
            "longitude": 83.4173236,
        },
        {
            "name": "Queens NRI Hospital",
            "type": "hospital",
            "address": "D.No. 5-1-11, Opp SBI Main Branch, Near NCS Theatre, Vizianagaram",
            "hostel_tag": DEFAULT_HOSTEL,
            "phone": "08922 251777",
            "open_hours": "24 Hours",
            # Vizianagaram Queens NRI branch coordinates
            "latitude": 18.1160657,
            "longitude": 83.4029738,
        },
        {
            "name": "Mahendra Hospitals",
            "type": "hospital",
            "address": "D.No. 1-15-1, Beside Aqua Sports Swimming Pool, RCM Church Road, Cantonment, Vizianagaram",
            "hostel_tag": DEFAULT_HOSTEL,
            "phone": "08922 222555",
            "open_hours": "24 Hours",
            # Approximate – refine later via Google Maps if you want
            "latitude": 18.1159,
            "longitude": 83.4025,
        },
        {
            "name": "Maharaja District Hospital",
            "type": "hospital",
            "address": "RCM Church Road, Vizianagaram",
            "hostel_tag": DEFAULT_HOSTEL,
            "phone": "08922 228800",
            "open_hours": "24 Hours (Govt.)",
            # Approximate
            "latitude": 18.1409,
            "longitude": 83.2987,
        },
        {
            "name": "Venkata Rama Hospital",
            "type": "hospital",
            "address": "Opp RTC Complex, Vizianagaram",
            "hostel_tag": DEFAULT_HOSTEL,
            "phone": "08922 273777",
            "open_hours": "24 Hours",
            # Approximate near RTC complex / Balaji Nagar
            "latitude": 18.1185,
            "longitude": 83.4045,
        },
        {
            "name": "Pushpagiri Eye Hospital",
            "type": "hospital",
            "address": "Near TTD Kalyana Mandapam, Alaknagar, Vizianagaram",
            "hostel_tag": DEFAULT_HOSTEL,
            "phone": "08922 270070",
            "open_hours": "9 AM - 8 PM",
            # Verified (Pushpagiri Eye Hospital, Alaknagar)
            "latitude": 18.115508,
            "longitude": 83.411954,
        },
        {
            "name": "Vamsi Children Hospital",
            "type": "hospital",
            "address": "Vizianagaram",
            "hostel_tag": DEFAULT_HOSTEL,
            "phone": "9440193885",
            "open_hours": "24 Hours (Pediatrics)",
            # Approximate
            "latitude": 18.1170,
            "longitude": 83.3990,
        },
        {
            "name": "PG Star Hospital",
            "type": "hospital",
            "address": "Rangala Street, Ramanaidu Road, Vizianagaram",
            "hostel_tag": DEFAULT_HOSTEL,
            "phone": "08922 272727",
            "open_hours": "24 Hours",
            # Approximate
            "latitude": 18.1115,
            "longitude": 83.4060,
        },
        {
            "name": "A J Global Health Care Hospital",
            "type": "hospital",
            "address": "Beside Bhashyam School, 100 Feet Ring Road, Vinayaka Nagar, Vizianagaram",
            "hostel_tag": DEFAULT_HOSTEL,
            "phone": "08922 299911",
            "open_hours": "24 Hours",
            # Approximate around 100 Ft Ring Road / Vinayaka Nagar
            "latitude": 18.1300,
            "longitude": 83.3880,
        },
        {
            "name": "MIMS Hospital, Nellimarla",
            "type": "hospital",
            "address": "Nellimarla, Vizianagaram",
            "hostel_tag": DEFAULT_HOSTEL,
            "phone": "08922 240777",
            "open_hours": "24 Hours",
            # Verified (MIMS Hospital, Nellimarla)
            "latitude": 18.146964,
            "longitude": 83.445320,
        },

        # ---------- PHARMACIES / MEDICAL SHOPS (5) ---------- #
        {
            "name": "Apollo Pharmacy - MG Road",
            "type": "medical_shop",
            "address": "Sri Sai Complex, MG Road, Vizianagaram",
            "hostel_tag": DEFAULT_HOSTEL,
            "phone": "08922 279999",
            "open_hours": "24 Hours",
            # Verified Apollo Pharmacy in Vizianagaram (MG Road area)
            "latitude": 18.1244906,
            "longitude": 83.3874123,
        },
        {
            "name": "MedPlus Pharmacy - Vizianagaram",
            "type": "medical_shop",
            "address": "Near Market Area, Vizianagaram",
            "hostel_tag": DEFAULT_HOSTEL,
            "phone": "08922 278888",
            "open_hours": "8 AM - 10 PM",
            # One of the MedPlus branches listed for Vizianagaram
            "latitude": 18.1017172,
            "longitude": 83.3927211,
        },
        {
            "name": "Datta Pharmacy",
            "type": "medical_shop",
            "address": "D.No. 5-15-14, Kothagraharam, Vizianagaram Market",
            "hostel_tag": DEFAULT_HOSTEL,
            "phone": "08922 270123",
            "open_hours": "9 AM - 10 PM",
            # Approximate near Kotha Agraharam / Market
            "latitude": 18.1105,
            "longitude": 83.4008,
        },
        {
            "name": "MS Satyanarayana Pharmacy",
            "type": "medical_shop",
            "address": "Near SKP Temple, Vizianagaram Market",
            "hostel_tag": DEFAULT_HOSTEL,
            "phone": "08922 271234",
            "open_hours": "9 AM - 10 PM",
            # Approximate around SKP Temple / Market
            "latitude": 18.1110,
            "longitude": 83.4020,
        },
        {
            "name": "Pradhan Mantri Bhartiya Janaushadhi Kendra - Bodduvari Junction",
            "type": "medical_shop",
            "address": "MRO Office Road, Bodduvari Junction, Vizianagaram",
            "hostel_tag": DEFAULT_HOSTEL,
            "phone": "08922 276543",
            "open_hours": "9 AM - 9 PM",
            # Approximate around Bodduvari Junction / MRO Road
            "latitude": 18.1150,
            "longitude": 83.3965,
        },
    ]
