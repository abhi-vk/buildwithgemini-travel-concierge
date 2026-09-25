from google.cloud import firestore

# CRITICAL: Hardcode the project ID as a string for Firestore client initialization
FIRESTORE_PROJECT_ID = "qwiklabs-gcp-01-25d8860bbf95"

def get_firestore_client():
    return firestore.Client(project=FIRESTORE_PROJECT_ID)

def search_destinations(city: str = "", category: str = "") -> list[dict]:
    """Search travel destinations stored in Firestore filtered by city or category.

    Args:
        city: Optional city name to filter destinations (e.g. 'San Francisco', 'New York').
        category: Optional destination category (e.g. 'Landmark', 'National Park', 'Urban Park').

    Returns:
        A list of destination dictionaries containing details like name, city, category, description, and rating.
    """
    db = get_firestore_client()
    collection_ref = db.collection("destinations")
    
    docs = collection_ref.stream()
    results = []
    
    city_lower = city.lower().strip() if city else ""
    category_lower = category.lower().strip() if category else ""

    for doc in docs:
        data = doc.to_dict()
        doc_city = str(data.get("city", "")).lower()
        doc_category = str(data.get("category", "")).lower()

        if city_lower and city_lower not in doc_city:
            continue
        if category_lower and category_lower not in doc_category:
            continue

        results.append({
            "id": doc.id,
            "name": data.get("name"),
            "city": data.get("city"),
            "category": data.get("category"),
            "description": data.get("description"),
            "rating": data.get("rating"),
            "tags": data.get("tags", [])
        })

    return results

def get_destination_details(name: str) -> dict:
    """Get detailed information about a specific travel destination by name.

    Args:
        name: Name of the destination to look up (e.g. 'Golden Gate Bridge', 'Central Park').

    Returns:
        A dictionary with the destination details, or an error message if not found.
    """
    db = get_firestore_client()
    collection_ref = db.collection("destinations")
    
    name_lower = name.lower().strip()
    docs = collection_ref.stream()

    for doc in docs:
        data = doc.to_dict()
        doc_name = str(data.get("name", "")).lower()
        if name_lower in doc_name or doc_name in name_lower:
            return {
                "id": doc.id,
                "name": data.get("name"),
                "city": data.get("city"),
                "category": data.get("category"),
                "description": data.get("description"),
                "rating": data.get("rating"),
                "tags": data.get("tags", [])
            }

    return {"error": f"No destination found matching '{name}'."}

def add_destination(
    name: str,
    city: str,
    category: str,
    description: str,
    rating: float = 4.5,
    tags: str = ""
) -> dict:
    """Add a new travel destination to the Firestore database catalog.

    Args:
        name: Name of the destination/attraction (e.g., 'Alcatraz Island').
        city: City where it is located (e.g., 'San Francisco').
        category: Category of the destination (e.g., 'Historical Site', 'Beach').
        description: Description of the destination.
        rating: Optional rating score out of 5 (default 4.5).
        tags: Optional comma-separated list of tags (e.g., 'history,tour,scenic').

    Returns:
        A dictionary confirming the newly created destination details.
    """
    db = get_firestore_client()
    collection_ref = db.collection("destinations")

    doc_id = name.lower().replace(" ", "-").replace("'", "")
    tag_list = [t.strip() for t in tags.split(",") if t.strip()] if isinstance(tags, str) else tags

    new_doc = {
        "name": name,
        "city": city,
        "category": category,
        "description": description,
        "rating": float(rating),
        "tags": tag_list or []
    }

    collection_ref.document(doc_id).set(new_doc)
    return {"status": "success", "id": doc_id, "destination": new_doc}
