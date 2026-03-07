from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.db.database import get_db
from app.models.session import Session as SessionModel
from app.schemas.session_schema import SessionCreate, SessionUpdate, Session as SessionSchema

router = APIRouter(prefix="/sessions", tags=["sessions"])

@router.post("", response_model=SessionSchema, status_code=status.HTTP_201_CREATED)
async def create_session(session: SessionCreate, db: Session = Depends(get_db)):
    """Create a new session"""
    db_session = SessionModel(**session.model_dump())
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session

@router.get("", response_model=List[SessionSchema])
async def list_sessions(db: Session = Depends(get_db)):
    """List all sessions"""
    sessions = db.query(SessionModel).all()
    return sessions

@router.get("/{session_id}", response_model=SessionSchema)
async def get_session(session_id: UUID, db: Session = Depends(get_db)):
    """Get a specific session by ID"""
    session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    return session

@router.put("/{session_id}", response_model=SessionSchema)
async def update_session(session_id: UUID, session_update: SessionUpdate, db: Session = Depends(get_db)):
    """Update a session"""
    session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    
    update_data = session_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(session, field, value)
    
    db.commit()
    db.refresh(session)
    return session

@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_session(session_id: UUID, db: Session = Depends(get_db)):
    """Delete a session"""
    session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    
    db.delete(session)
    db.commit()
    return None
