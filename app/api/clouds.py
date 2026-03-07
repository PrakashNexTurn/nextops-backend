from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.db.database import get_db
from app.models.cloud_account import CloudAccount
from app.schemas.session_schema import CloudAccountCreate, CloudAccountUpdate, CloudAccount as CloudAccountSchema

router = APIRouter(prefix="/clouds", tags=["clouds"])

@router.post("", response_model=CloudAccountSchema, status_code=status.HTTP_201_CREATED)
async def create_cloud_account(cloud_account: CloudAccountCreate, db: Session = Depends(get_db)):
    """Register a new cloud account"""
    db_cloud = CloudAccount(**cloud_account.model_dump())
    db.add(db_cloud)
    db.commit()
    db.refresh(db_cloud)
    return db_cloud

@router.get("", response_model=List[CloudAccountSchema])
async def list_cloud_accounts(db: Session = Depends(get_db)):
    """List all cloud accounts"""
    clouds = db.query(CloudAccount).all()
    return clouds

@router.get("/{cloud_id}", response_model=CloudAccountSchema)
async def get_cloud_account(cloud_id: UUID, db: Session = Depends(get_db)):
    """Get a specific cloud account by ID"""
    cloud = db.query(CloudAccount).filter(CloudAccount.id == cloud_id).first()
    if not cloud:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cloud account not found")
    return cloud

@router.put("/{cloud_id}", response_model=CloudAccountSchema)
async def update_cloud_account(cloud_id: UUID, cloud_update: CloudAccountUpdate, db: Session = Depends(get_db)):
    """Update a cloud account"""
    cloud = db.query(CloudAccount).filter(CloudAccount.id == cloud_id).first()
    if not cloud:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cloud account not found")
    
    update_data = cloud_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(cloud, field, value)
    
    db.commit()
    db.refresh(cloud)
    return cloud

@router.delete("/{cloud_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_cloud_account(cloud_id: UUID, db: Session = Depends(get_db)):
    """Delete a cloud account"""
    cloud = db.query(CloudAccount).filter(CloudAccount.id == cloud_id).first()
    if not cloud:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cloud account not found")
    
    db.delete(cloud)
    db.commit()
    return None
