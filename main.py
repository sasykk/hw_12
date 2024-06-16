import crud
import schemas
from sqlalchemy.orm import Session
from auth import router as auth_router
from database import engine, Base, get_db
from fastapi.security import OAuth2PasswordBearer
from fastapi import FastAPI, Depends, HTTPException, status

Base.metadata.create_all(bind=engine)

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

app.include_router(auth_router, prefix="/auth", tags=["auth"])

@app.post("/contacts/", response_model=schemas.Contact)
def create_contact(contact: schemas.ContactCreate, db: Session = Depends(get_db),
                   current_user: schemas.User = Depends(crud.get_current_active_user)):
    return crud.create_contact(db=db, contact=contact, user_id=current_user.id)

@app.get("/contacts/", response_model=list[schemas.Contact])
def read_contacts(skip: int = 0, limit: int = 10, db: Session = Depends(get_db),
                  current_user: schemas.User = Depends(crud.get_current_active_user)):

    return crud.get_contacts(db, skip=skip, limit=limit, user_id=current_user.id)

@app.get("/contacts/{contact_id}", response_model=schemas.Contact)
def read_contact(contact_id: int, db: Session = Depends(get_db),
                 current_user: schemas.User = Depends(crud.get_current_active_user)):
    db_contact = crud.get_contact(db, contact_id=contact_id)
    if db_contact is None or db_contact.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Contact not found")
    return db_contact

@app.put("/contacts/{contact_id}", response_model=schemas.Contact)
def update_contact(contact_id: int, contact: schemas.ContactUpdate,
                   db: Session = Depends(get_db), current_user: schemas.User = Depends(crud.get_current_active_user)):
    db_contact = crud.get_contact(db, contact_id=contact_id)
    if db_contact is None or db_contact.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return crud.update_contact(db=db, contact_id=contact_id, contact=contact)

@app.delete("/contacts/{contact_id}", response_model=schemas.Contact)
def delete_contact(contact_id: int, db: Session = Depends(get_db),
                   current_user: schemas.User = Depends(crud.get_current_active_user)):
    db_contact = crud.delete_contact(db, contact_id=contact_id)
    if db_contact is None or db_contact.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Contact not found")
    return db_contact

@app.get("/contacts/search/", response_model=list[schemas.Contact])
def search_contacts(query: str, db: Session = Depends(get_db),
                    current_user: schemas.User = Depends(crud.get_current_active_user)):
    return crud.search_contacts(db, query=query, user_id=current_user.id)


@app.get("/contacts/upcoming_birthdays/", response_model=list[schemas.Contact])
def get_upcoming_birthdays(db: Session = Depends(get_db),
                           current_user: schemas.User = Depends(crud.get_current_active_user)):
    return crud.get_upcoming_birthdays(db, user_id=current_user.id)
