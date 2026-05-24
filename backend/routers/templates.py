from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from database import get_db
from models import Template
from schemas import TemplateCreate, TemplateUpdate, TemplateResponse

router = APIRouter()


@router.get("", response_model=dict)
def list_templates(db: Session = Depends(get_db)):
    templates = db.query(Template).order_by(Template.created_at).all()
    return {
        "data": [TemplateResponse.model_validate(t).model_dump() for t in templates],
        "message": "ok",
    }


@router.post("", response_model=dict)
def create_template(tmpl_in: TemplateCreate, db: Session = Depends(get_db)):
    template = Template(**tmpl_in.model_dump())
    db.add(template)
    db.commit()
    db.refresh(template)
    return {"data": TemplateResponse.model_validate(template).model_dump(), "message": "Template created"}


@router.get("/{template_id}", response_model=dict)
def get_template(template_id: int, db: Session = Depends(get_db)):
    template = db.query(Template).get(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return {"data": TemplateResponse.model_validate(template).model_dump(), "message": "ok"}


@router.put("/{template_id}", response_model=dict)
def update_template(template_id: int, tmpl_in: TemplateUpdate, db: Session = Depends(get_db)):
    template = db.query(Template).get(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    for field, value in tmpl_in.model_dump(exclude_unset=True).items():
        setattr(template, field, value)

    template.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(template)
    return {"data": TemplateResponse.model_validate(template).model_dump(), "message": "Template updated"}


@router.delete("/{template_id}", response_model=dict)
def delete_template(template_id: int, db: Session = Depends(get_db)):
    template = db.query(Template).get(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    db.delete(template)
    db.commit()
    return {"data": None, "message": "Template deleted"}
