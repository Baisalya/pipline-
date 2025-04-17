from azure.storage.blob import BlobServiceClient, ContentSettings
from .config import AZURE_CONNECTION_STRING, CONTAINER_NAME
import uuid

blob_service_client = BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)
container_client = blob_service_client.get_container_client(CONTAINER_NAME)

# Ensure container exists
try:
    container_client.create_container()
    print("✅ Azure Blob Storage Connected Successfully!")
except Exception:
    pass  # already exists
    print("⚠️ Azure Blob Container Already Exists or Connection Failed!")
def upload_pipeline_json(data: dict) -> str:
    json_data = json.dumps(data, indent=4)
    blob_name = f"pipeline_json/{uuid.uuid4()}.json"
    blob_client = container_client.get_blob_client(blob_name)
    blob_client.upload_blob(
        json_data,
        blob_type="BlockBlob",
        content_settings=ContentSettings(content_type="application/json")
    )
    return blob_client.url

def delete_pipeline_json_by_url(json_url: str):
    blob_name = json_url.split("/")[-1]
    blob_client = container_client.get_blob_client(f"pipeline_json/{blob_name}")
    blob_client.delete_blob()
