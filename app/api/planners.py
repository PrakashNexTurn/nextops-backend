from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.db.database import get_db
from app.models.planner import Planner
from app.models.planner_agent import PlannerAgent
from app.schemas.planner_schema import PlannerCreate, PlannerUpdate, Planner as PlannerSchema

router = APIRouter(prefix="/planners", tags=["planners"])

@router.post("", response_model=PlannerSchema, status_code=status.HTTP_201_CREATED)
async def create_planner(planner: PlannerCreate, db: Session = Depends(get_db)):
    """Create a new planner agent"""
    db_planner = Planner(
        name=planner.name,
        system_prompt=planner.system_prompt,
        tags=planner.tags
    )
    db.add(db_planner)
    db.flush()
    
    # Add planner agents
    if planner.agents:
        for agent_id in planner.agents:
            planner_agent = PlannerAgent(planner_id=db_planner.id, agent_id=agent_id)
            db.add(planner_agent)
    
    db.commit()
    db.refresh(db_planner)
    return db_planner

@router.get("", response_model=List[PlannerSchema])
async def list_planners(db: Session = Depends(get_db)):
    """List all planners"""
    planners = db.query(Planner).all()
    return planners

@router.get("/{planner_id}", response_model=PlannerSchema)
async def get_planner(planner_id: UUID, db: Session = Depends(get_db)):
    """Get a specific planner by ID"""
    planner = db.query(Planner).filter(Planner.id == planner_id).first()
    if not planner:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Planner not found")
    return planner

@router.put("/{planner_id}", response_model=PlannerSchema)
async def update_planner(planner_id: UUID, planner_update: PlannerUpdate, db: Session = Depends(get_db)):
    """Update a planner"""
    planner = db.query(Planner).filter(Planner.id == planner_id).first()
    if not planner:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Planner not found")
    
    update_data = planner_update.model_dump(exclude_unset=True, exclude={"agents"})
    for field, value in update_data.items():
        setattr(planner, field, value)
    
    # Update agents if provided
    if planner_update.agents is not None:
        db.query(PlannerAgent).filter(PlannerAgent.planner_id == planner_id).delete()
        for agent_id in planner_update.agents:
            planner_agent = PlannerAgent(planner_id=planner_id, agent_id=agent_id)
            db.add(planner_agent)
    
    db.commit()
    db.refresh(planner)
    return planner

@router.delete("/{planner_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_planner(planner_id: UUID, db: Session = Depends(get_db)):
    """Delete a planner"""
    planner = db.query(Planner).filter(Planner.id == planner_id).first()
    if not planner:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Planner not found")
    
    db.delete(planner)
    db.commit()
    return None

@router.post("/{planner_id}/agents/{agent_id}", status_code=status.HTTP_201_CREATED)
async def add_agent_to_planner(planner_id: UUID, agent_id: UUID, db: Session = Depends(get_db)):
    """Add an agent to a planner"""
    planner = db.query(Planner).filter(Planner.id == planner_id).first()
    if not planner:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Planner not found")
    
    existing = db.query(PlannerAgent).filter(
        PlannerAgent.planner_id == planner_id,
        PlannerAgent.agent_id == agent_id
    ).first()
    
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Agent already assigned to planner")
    
    planner_agent = PlannerAgent(planner_id=planner_id, agent_id=agent_id)
    db.add(planner_agent)
    db.commit()
    return {"message": "Agent added to planner"}

@router.delete("/{planner_id}/agents/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_agent_from_planner(planner_id: UUID, agent_id: UUID, db: Session = Depends(get_db)):
    """Remove an agent from a planner"""
    planner_agent = db.query(PlannerAgent).filter(
        PlannerAgent.planner_id == planner_id,
        PlannerAgent.agent_id == agent_id
    ).first()
    
    if not planner_agent:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Planner agent not found")
    
    db.delete(planner_agent)
    db.commit()
    return None
