import json
import os
import urllib.parse
import urllib.request
from dotenv import load_dotenv

# Load .env file automatically
load_dotenv()

def geocode_address(address: str) -> dict:
    """Convert an address or location name into geographic coordinates (latitude and longitude) using Google Geocoding API.

    Args:
        address: The address, city, or landmark name to geocode (e.g., '1600 Amphitheatre Pkwy, Mountain View, CA' or 'Golden Gate Bridge').

    Returns:
        A dictionary containing the formatted address, location coordinates (lat, lng), and place_id.
    """
    api_key = os.environ.get("GOOGLE_MAPS_API_KEY", "").strip()
    if not api_key or api_key == "PASTE_KEY_HERE":
        return {
            "error": "GOOGLE_MAPS_API_KEY is not set or contains default placeholder. Please update GOOGLE_MAPS_API_KEY in .env."
        }

    encoded_address = urllib.parse.quote(address)
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={encoded_address}&key={api_key}"

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "TravelConciergeAgent/1.0"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode())
            if data.get("status") == "OK" and data.get("results"):
                result = data["results"][0]
                loc = result.get("geometry", {}).get("location", {})
                return {
                    "status": "success",
                    "address": result.get("formatted_address", address),
                    "location": {
                        "latitude": loc.get("lat"),
                        "longitude": loc.get("lng"),
                    },
                    "place_id": result.get("place_id"),
                }
            else:
                return {
                    "error": f"Geocoding API status: {data.get('status')}",
                    "details": data.get("error_message", "No results found"),
                }
    except Exception as e:
        return {"error": f"Failed to call Geocoding API: {str(e)}"}


def find_nearby_places(
    latitude: float,
    longitude: float,
    place_type: str = "restaurant",
    radius_meters: float = 1000.0,
) -> dict:
    """Find nearby places of a specific type around coordinates using the Google Places API (New).

    Args:
        latitude: Latitude of the center point (e.g. 37.7749).
        longitude: Longitude of the center point (e.g. -122.4194).
        place_type: Type of place to search for (e.g. 'restaurant', 'cafe', 'museum', 'park', 'tourist_attraction').
        radius_meters: Search radius in meters (default 1000.0 meters).

    Returns:
        A dictionary containing a list of nearby places with key fields: name, address, and location.
    """
    api_key = os.environ.get("GOOGLE_MAPS_API_KEY", "").strip()
    if not api_key or api_key == "PASTE_KEY_HERE":
        return {
            "error": "GOOGLE_MAPS_API_KEY is not set or contains default placeholder. Please update GOOGLE_MAPS_API_KEY in .env."
        }

    url = "https://places.googleapis.com/v1/places:searchNearby"
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.location,places.types",
        "User-Agent": "TravelConciergeAgent/1.0",
    }
    payload = {
        "includedTypes": [place_type],
        "maxResultCount": 5,
        "locationRestriction": {
            "circle": {
                "center": {
                    "latitude": float(latitude),
                    "longitude": float(longitude),
                },
                "radius": float(radius_meters),
            }
        },
    }

    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode())
            places_list = []
            for p in data.get("places", []):
                disp_name = p.get("displayName", {}).get("text", "Unknown Place")
                fmt_addr = p.get("formattedAddress", "")
                loc = p.get("location", {})
                places_list.append(
                    {
                        "name": disp_name,
                        "address": fmt_addr,
                        "location": {
                            "latitude": loc.get("latitude"),
                            "longitude": loc.get("longitude"),
                        },
                    }
                )
            return {
                "status": "success",
                "count": len(places_list),
                "places": places_list,
            }
    except Exception as e:
        return {"error": f"Failed to call Places API (New): {str(e)}"}
