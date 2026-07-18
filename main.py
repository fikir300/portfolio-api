"""
Complete Backend API for Portfolio CMS.
Includes Create, Read, and Delete functionality with Image support.
"""
import os
import psycopg2
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# 1. Load configuration
load_dotenv()
app = FastAPI()

# 2. Enable CORS so your website can talk to this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DATABASE_URL = os.getenv("DATABASE_URL")

def get_db_connection():
    """Helper function to connect to Neon Database."""
    return psycopg2.connect(DATABASE_URL)

# 3. The Data Model (Includes the new image_url)
class Project(BaseModel):
    """Data structure for a portfolio project."""
    title: str
    description: str
    link: str
    tech_stack: str
    image_url: str

@app.get("/")
def home():
    """Verify the API is running."""
    return {"status": "Portfolio API is live!"}

# 4. GET endpoint: Read projects
@app.get("/projects")
def get_projects():
    """Retrieve all projects from the database."""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM projects ORDER BY id DESC")
                columns = [desc[0] for desc in cur.description]
                results = [dict(zip(columns, row)) for row in cur.fetchall()]
                return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e

# 5. POST endpoint: Add a new project
@app.post("/projects")
def create_project(project: Project):
    """Add a new project with an image link."""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                sql = """
                INSERT INTO projects (title, description, link, tech_stack, image_url) 
                VALUES (%s, %s, %s, %s, %s)
                """
                cur.execute(
                    sql, 
                    (project.title, project.description, project.link, project.tech_stack, project.image_url)
                )
                conn.commit()
                return {"message": "Project added successfully!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e

# 6. DELETE endpoint: Remove a project
@app.delete("/projects/{project_id}")
def delete_project(project_id: int):
    """Delete a project using its ID."""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM projects WHERE id = %s", (project_id,))
                conn.commit()
                return {"message": f"Project {project_id} deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
