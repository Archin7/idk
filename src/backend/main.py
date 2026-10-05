import psycopg2
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Define the Note model
class Note(BaseModel):
    title: str
    content: str


with open("sysusrname.txt", "r") as f:
    username = f.read().strip()


def get_connection():
    return psycopg2.connect(
        host="localhost",
        database="notes_app",
        user=username,
    )


@app.get("/notes")
def getAll():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, content FROM notes")
    all_notes = cursor.fetchall()
    cursor.close()
    conn.close()

    return [{"id": row[0], "title": row[1], "content": row[2]} for row in all_notes]


@app.post("/notes")
def create_note(note: Note) -> dict[str, str | int]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO notes (title, content) VALUES (%s, %s) RETURNING id",
        (note.title, note.content),
    )

    new_id = cursor.fetchone()[0]  # pyright: ignore[reportUnknownVariableType, reportOptionalSubscript]
    conn.commit()

    cursor.close()
    conn.close()

    return {"id": new_id, "title": note.title, "content": note.content}


@app.put("/notes/{note_id}")
def update_note(note_id: int, note: Note):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE notes SET title = %s, content = %s WHERE id = %s",
        (note.title, note.content, note_id),
    )
    conn.commit()
    cursor.close()
    conn.close()
    return {"status": "updated"}


@app.delete("/notes/{note_id}")
def delete_note(note_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM notes WHERE id = %s", (note_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return {"status": "deleted"}
