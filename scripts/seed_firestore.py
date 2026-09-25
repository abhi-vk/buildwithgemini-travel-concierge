import os
from google.cloud import firestore

# CRITICAL: Hardcode the project ID as a string so it uses the project ID (not the project number)
FIRESTORE_PROJECT_ID = "qwiklabs-gcp-01-25d8860bbf95"

def seed_database():
    print(f"Connecting to Firestore for project: {FIRESTORE_PROJECT_ID}")
    db = firestore.Client(project=FIRESTORE_PROJECT_ID)
    collection_ref = db.collection("destinations")

    sample_destinations = [
        {
            "id": "sf-golden-gate",
            "name": "Golden Gate Bridge",
            "city": "San Francisco",
            "category": "Landmark",
            "description": "Iconic red suspension bridge connecting San Francisco Bay and the Pacific Ocean. Great for walking, biking, and photography.",
            "rating": 4.9,
            "tags": ["iconic", "scenic", "outdoors", "photography"]
        },
        {
            "id": "sf-coit-tower",
            "name": "Coit Tower",
            "city": "San Francisco",
            "category": "Landmark",
            "description": "Art deco tower atop Telegraph Hill offering 360-degree panoramic views of San Francisco and murals inside.",
            "rating": 4.6,
            "tags": ["views", "history", "art"]
        },
        {
            "id": "ny-central-park",
            "name": "Central Park",
            "city": "New York",
            "category": "Urban Park",
            "description": "Expansive urban oasis in Manhattan featuring rowboats, walking paths, concerts, and historical monuments.",
            "rating": 4.8,
            "tags": ["outdoors", "scenic", "family-friendly"]
        },
        {
            "id": "yosemite-valley",
            "name": "Yosemite Valley",
            "city": "Yosemite",
            "category": "National Park",
            "description": "Glacial valley framed by granite summits El Capitan and Half Dome, featuring grand waterfalls and giant sequoias.",
            "rating": 4.95,
            "tags": ["nature", "hiking", "scenic", "outdoors"]
        }
    ]

    for data in sample_destinations:
        doc_data = dict(data)
        doc_id = doc_data.pop("id")
        doc_ref = collection_ref.document(doc_id)
        doc_ref.set(doc_data)
        print(f"Seeded destination: {doc_id} -> {doc_data['name']}")

    print("Firestore seeding complete!")

if __name__ == "__main__":
    seed_database()
