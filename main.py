"""
Main API module for the Portfolio Content Management System.
Handles project retrieval and internal management.
"""
import os
import psycopg2
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Enable CORS for frontend interaction
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DATABASE_URL = os.getenv("DATABASE_URL")


def get_db_connection():
    """Create and return a database connection."""
    return psycopg2.connect(DATABASE_URL)


class Project(BaseModel):
    """Data model for a portfolio project."""
    title: str
    description: str
    link: str
    tech_stack: str


@app.get("/")
def home():
    """Root endpoint to verify the API status."""
    return {"status": "Portfolio API is live!"}


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


@app.post("/projects")
def create_project(project: Project):
    """Add a new project to the database."""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                sql = """
                INSERT INTO projects (title, description, link, tech_stack)
                VALUES (%s, %s, %s, %s)
                """
                cur.execute(
                    sql,
                    (project.title, project.description, project.link, project.tech_stack)
                )
                conn.commit()
                return {"message": "Project added successfully!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
