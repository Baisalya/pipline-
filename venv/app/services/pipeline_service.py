from ..database import get_db_connection
from ..azure_blob import upload_pipeline_json, delete_pipeline_json_by_url

def create_pipeline(pipeline_name: str, status: str, canvas_name: str):
    conn = get_db_connection()
    cursor = conn.cursor()

    data = {
        "pipeline_name": pipeline_name,
        "status": status,
        "canvas_name": canvas_name
    }

    json_url = upload_pipeline_json(data)

    cursor.execute(
        "INSERT INTO Pipeline (pipeline_name, status, canvas_name, json_url) VALUES (?, ?, ?, ?)",
        (pipeline_name, status, canvas_name, json_url),
    )
    conn.commit()
    conn.close()
    return {"message": "Pipeline created successfully", "json_url": json_url}

def get_all_pipelines():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, pipeline_name, status, canvas_name, json_url FROM Pipeline")
    pipelines = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]
    conn.close()
    return pipelines

def get_pipeline_by_id(pipeline_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, pipeline_name, status, canvas_name, json_url FROM Pipeline WHERE id = ?", (pipeline_id,))
    pipeline = cursor.fetchone()
    conn.close()
    if not pipeline:
        return None
    return dict(zip([column[0] for column in cursor.description], pipeline))

def delete_pipeline(pipeline_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT json_url FROM Pipeline WHERE id = ?", (pipeline_id,))
    pipeline = cursor.fetchone()
    if not pipeline:
        conn.close()
        return None
    json_url = pipeline[0]
    delete_pipeline_json_by_url(json_url)

    cursor.execute("DELETE FROM Pipeline WHERE id = ?", (pipeline_id,))
    conn.commit()
    conn.close()
    return {"message": "Pipeline deleted successfully"}
