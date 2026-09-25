import base64
import re
import time
from google import genai
from google.cloud import storage
from google.genai import types
from google.adk.tools import ToolContext

# Hardcoded GCP Project ID and GCS Bucket Name as requested
PROJECT_ID = "qwiklabs-gcp-01-25d8860bbf95"
BUCKET_NAME = "travel-concierge-media-qwiklabs-gcp-01-25d8860bbf95"

def generate_destination_video(
    prompt: str,
    destination_name: str = "destination",
    tool_context: ToolContext = None,
) -> dict:
    """Generate a short video clip of a travel destination or venue using gemini-omni-flash-preview in the global region.

    This tool performs two actions with the generated video:
    1. Saves the video via tool_context.save_artifact for the Playground Artifacts panel.
    2. Uploads the video bytes to public Cloud Storage and returns its public https URL.

    Args:
        prompt: Detailed description of the video to generate (e.g. 'A short video of ocean waves at sunset in Hawaii').
        destination_name: Name of the destination or venue.
        tool_context: ADK ToolContext provided automatically by the runtime.

    Returns:
        A dictionary containing the video's public GCS https URL and artifact status.
    """
    try:
        genai_client = genai.Client(vertexai=True, project=PROJECT_ID, location="global")
        response = genai_client.interactions.create(
            model="gemini-omni-flash-preview",
            input=prompt,
        )

        video_bytes = None
        mime_type = "video/mp4"

        if hasattr(response, "output_video") and response.output_video:
            if getattr(response.output_video, "data", None):
                video_bytes = base64.b64decode(response.output_video.data)
            if getattr(response.output_video, "mime_type", None):
                mime_type = response.output_video.mime_type

        if not video_bytes:
            return {"error": "Failed to generate video bytes from model response."}

        safe_name = re.sub(r"[^a-zA-Z0-9_-]", "_", destination_name.lower())
        filename = f"{safe_name}_{int(time.time())}.mp4"

        # 1. Save with tool_context.save_artifact for Playground Artifacts panel
        artifact_saved = False
        if tool_context is not None:
            artifact_part = types.Part.from_bytes(data=video_bytes, mime_type=mime_type)
            tool_context.save_artifact(filename=filename, artifact=artifact_part)
            artifact_saved = True

        # 2. Upload video bytes to public Cloud Storage bucket
        storage_client = storage.Client(project=PROJECT_ID)
        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(f"videos/{filename}")
        blob.upload_from_string(video_bytes, content_type=mime_type)

        public_url = f"https://storage.googleapis.com/{BUCKET_NAME}/videos/{filename}"

        return {
            "status": "success",
            "destination_name": destination_name,
            "public_url": public_url,
            "artifact_saved": artifact_saved,
            "filename": filename,
        }
    except Exception as e:
        return {"error": f"Failed to generate destination video: {str(e)}"}
