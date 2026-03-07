from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.db.database import get_db
from app.models.deployment import Deployment
from app.schemas.session_schema import DeploymentCreate, DeploymentUpdate, Deployment as DeploymentSchema

router = APIRouter(prefix="/deployments", tags=["deployments"])

@router.post("", response_model=DeploymentSchema, status_code=status.HTTP_201_CREATED)
async def create_deployment(deployment: DeploymentCreate, db: Session = Depends(get_db)):
    """Create a new deployment"""
    db_deployment = Deployment(
        agent_id=deployment.agent_id,
        deployment_type=deployment.deployment_type,
        status="pending"
    )
    db.add(db_deployment)
    db.commit()
    db.refresh(db_deployment)
    return db_deployment

@router.get("", response_model=List[DeploymentSchema])
async def list_deployments(db: Session = Depends(get_db)):
    """List all deployments"""
    deployments = db.query(Deployment).all()
    return deployments

@router.get("/{deployment_id}", response_model=DeploymentSchema)
async def get_deployment(deployment_id: UUID, db: Session = Depends(get_db)):
    """Get a specific deployment by ID"""
    deployment = db.query(Deployment).filter(Deployment.id == deployment_id).first()
    if not deployment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Deployment not found")
    return deployment

@router.put("/{deployment_id}", response_model=DeploymentSchema)
async def update_deployment(deployment_id: UUID, deployment_update: DeploymentUpdate, db: Session = Depends(get_db)):
    """Update a deployment"""
    deployment = db.query(Deployment).filter(Deployment.id == deployment_id).first()
    if not deployment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Deployment not found")
    
    update_data = deployment_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(deployment, field, value)
    
    db.commit()
    db.refresh(deployment)
    return deployment

@router.delete("/{deployment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_deployment(deployment_id: UUID, db: Session = Depends(get_db)):
    """Delete a deployment"""
    deployment = db.query(Deployment).filter(Deployment.id == deployment_id).first()
    if not deployment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Deployment not found")
    
    db.delete(deployment)
    db.commit()
    return None
