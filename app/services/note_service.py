from sqlalchemy.orm import Session
from app.repositories.note_repo import NoteRepository


class NoteService:
    def __init__(self, db: Session):
        self.repo = NoteRepository
