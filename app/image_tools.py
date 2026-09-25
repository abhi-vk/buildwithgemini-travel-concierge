import re
import time
from google import genai
from google.cloud import storage
from google.genai import types
from google.adk.tools import ToolContext

# Hardcoded GCP Project ID and GCS Bucket Name as requested
PROJECT_ID = "qwiklabs-gcp-01-25d8860bbf95"
BUCKET_NAME = "travel-concierge-media-qwiklabs-gcp-01-25d8860bbf95"

def generate_destination_image(
    prompt: str,
    destination_name: str = "destination",
    tool_context: ToolContext = None,
) -> dict:
    """Generate a photo or postcard image of a travel destination using gemini-3.1-flash-lite-image in the global region.
    
    This tool performs two actions with the generated image:
    1. Saves the image via tool_context.save_artifact for the Playground Artifacts panel.
    2. Uploads the image bytes to public Cloud Storage and returns its public https URL.

    Args:
        prompt: Detailed description of the image to generate (e.g. 'A sunny postcard of Yosemite Valley').
        destination_name: Name of the destination.
        tool_context: ADK ToolContext provided automatically by the runtime.

    Returns:
        A dictionary containing the image's public GCS https URL and artifact status.
    """
    try:
        genai_client = genai.Client(vertexai=True, project=PROJECT_ID, location="global")
        response = genai_client.models.generate_content(
            model="gemini-3.1-flash-lite-image",
            contents=prompt,
        )

        image_bytes = None
        if response.candidates:
            for part in response.candidates[0].content.parts:
                if part.inline_data:
                    image_bytes = part.inline_data.data
                    break

        if not image_bytes:
            return {"error": "Failed to generate image bytes from model response."}

        safe_name = re.sub(r"[^a-zA-Z0-9_-]", "_", destination_name.lower())
        filename = f"{safe_name}_{int(time.time())}.jpg"

        # 1. Save with tool_context.save_artifact for Playground Artifacts panel
        artifact_saved = False
        if tool_context is not None:
            artifact_part = types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg")
            tool_context.save_artifact(filename=filename, artifact=artifact_part)
            artifact_saved = True

        # 2. Upload image bytes to public Cloud Storage bucket
        storage_client = storage.Client(project=PROJECT_ID)
        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(f"destinations/{filename}")
        blob.upload_from_string(image_bytes, content_type="image/jpeg")

        public_url = f"https://storage.googleapis.com/{BUCKET_NAME}/destinations/{filename}"

        return {
            "status": "success",
            "destination_name": destination_name,
            "public_url": public_url,
            "artifact_saved": artifact_saved,
            "filename": filename,
        }
    except Exception as e:
        return {"error": f"Failed to generate destination image: {str(e)}"}
