from fastapi import FastAPI, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
import pyodbc
import bcrypt
from azure.storage.blob import BlobServiceClient, ContentSettings
from dotenv import load_dotenv
import os
import uuid
import json

# Load environment variables
load_dotenv()

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database Configuration
DB_CONFIG = {
    "server": os.getenv("DB_SERVER"),
    "database": os.getenv("DB_DATABASE"),
    "username": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
}

# Azure Blob Storage Configuration
AZURE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
CONTAINER_NAME = "pipelines-json"

# Ensure Azure Blob Container Exists
try:
    blob_service_client = BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)
    container_client = blob_service_client.get_container_client(CONTAINER_NAME)
    container_client.create_container()
    print("✅ Azure Blob Storage Connected Successfully!")
except Exception:
    print("⚠️ Azure Blob Container Already Exists or Connection Failed!")

# Database Connection
def get_db_connection():
    try:
        conn = pyodbc.connect(
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={DB_CONFIG['server']};"
            f"DATABASE={DB_CONFIG['database']};"
            f"UID={DB_CONFIG['username']};"
            f"PWD={DB_CONFIG['password']}"
        )
        print("✅ Database Connected Successfully!")
        return conn
    except Exception as e:
        print(f"❌ Database Connection Failed: {str(e)}")
        return None

# Create a Pipeline Entry
@app.post("/pipelines")
async def create_pipeline(
    pipeline_name: str = Form(...), 
    status: str = Form(...), 
    canvas_name: str = Form(...)
):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Generate JSON Object
        pipeline_data = {
            "pipeline_name": pipeline_name,
            "status": status,
            "canvas_name": canvas_name
        }
        json_content = json.dumps(pipeline_data, indent=4)

        # Upload JSON to Blob Storage
        blob_name = f"pipeline_json/{uuid.uuid4()}.json"
        blob_client = container_client.get_blob_client(blob_name)
        blob_client.upload_blob(json_content, blob_type="BlockBlob", content_settings=ContentSettings(content_type="application/json"))
        json_url = blob_client.url

        # Insert into Database
        cursor.execute(
            "INSERT INTO Pipeline (pipeline_name, status, canvas_name, json_url) VALUES (?, ?, ?, ?)",
            (pipeline_name, status, canvas_name, json_url),
        )
        conn.commit()

        return {"message": "Pipeline created successfully", "json_url": json_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()
# Get All Pipelines
@app.get("/pipelines")
def get_pipelines():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, pipeline_name, status, canvas_name, json_url FROM Pipeline")
        pipelines = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]
        return pipelines
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

# Get Pipeline by ID
@app.get("/pipelines/{pipeline_id}")
def get_pipeline(pipeline_id: int):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, pipeline_name, status, canvas_name, json_url FROM Pipeline WHERE id = ?", (pipeline_id,))
        pipeline = cursor.fetchone()
        if not pipeline:
            raise HTTPException(status_code=404, detail="Pipeline not found")
        return dict(zip([column[0] for column in cursor.description], pipeline))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

# Delete Pipeline
@app.delete("/pipelines/{pipeline_id}")
def delete_pipeline(pipeline_id: int):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Get JSON URL before deleting entry
        cursor.execute("SELECT json FROM Pipeline WHERE id = ?", (pipeline_id,))
        pipeline = cursor.fetchone()
        if not pipeline:
            raise HTTPException(status_code=404, detail="Pipeline not found")
        json_url = pipeline[0]

        # Extract Blob Name and Delete from Storage
        blob_name = json_url.split("/")[-1]
        blob_client = container_client.get_blob_client(f"pipeline_json/{blob_name}")
        blob_client.delete_blob()

        # Delete from Database
        cursor.execute("DELETE FROM Pipeline WHERE id = ?", (pipeline_id,))
        conn.commit()
        return {"message": "Pipeline deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

# Home Route
@app.get("/")
def home():
    return {"message": "🚀 FastAPI Deployment Successful!"}

# Start the FastAPI Server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
