from sqlalchemy.orm import Session
from app.models.note import Note
from app.schemas.note import NoteCreate, NoteUpdate


class NoteRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_all_by_user(self, user_id: int) -> list[Note]:
        return self.db.query(Note).filter(Note.owner_id == user_id).all()

    def get_by_id(self, note_id: int) -> Note | None:
        return self.db.query(Note).filter(Note.id == note_id).first()

    def create(self, data: NoteCreate, user_id: int) -> Note:
        note = Note(
            title=data.title,
            content=data.content,
            owner_id=user_id,
        )
        self.db.add(note)
        self.db.commit()
        self.db.refresh(note)
        return note

    def update(self, note: Note, data: NoteUpdate) -> Note:
        if data.title is not None:
            note.title = data.title
        if data.content is not None:
            note.content = data.content
        self.db.commit()
        self.db.refresh(note)
        return note

    def delete(self, note: Note) -> None:
        self.db.delete(note)
        self.db.commit()
