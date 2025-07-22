from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from database import Base, engine, SessionLocal
from models import User, Device, GlucoseReading, ActivityLog, LabResult
from schemas import UserSchema, DeviceSchema, GlucoseReadingSchema, ActivityLogSchema, LabResultSchema
from datetime import datetime
from fastapi.responses import JSONResponse
from rule_engine import adjust_meals_for_user
import json

app = FastAPI()

Base.metadata.create_all(bind=engine)


# Dependency to get DB session

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def root():
    return {"message": "NutritionApp API is running"}


@app.get("/recommend-meals/{user_id}")
def recommend_meals(user_id: int):
    db: Session = SessionLocal()

    # Get lab results (HbA1c) for user
    labs = db.query(LabResult).filter(LabResult.user_id == user_id).all()
    lab_data = [{"test_type": l.test_type, "value": l.value} for l in labs]

    # Get total steps from today's activity log
    from datetime import date
    today = date.today().isoformat()

    steps_data = db.query(ActivityLog).filter(
        ActivityLog.user_id == user_id,
        ActivityLog.timestamp.startswith(today)
    ).all()

    total_steps = sum([a.steps or 0 for a in steps_data])

    # Load meals.json (mock catalog)
    with open("meals.json", "r") as f:
        meal_catalog = json.load(f)

    # Adjust meals using rule engine
    result = adjust_meals_for_user(lab_data, total_steps, meal_catalog)
    return {"user_id": user_id, "total_steps": total_steps, "meals": result}


@app.post("/users/", response_model=UserSchema)
def create_user(user: UserSchema, db: Session = Depends(get_db)):
    db_user = User(
        user_id=user.user_id,
        name=user.name or "Unknown",
        email=user.email or "Unknown",
        dob=user.dob,
        gender=user.gender or "Unknown",
        goal=user.goal or "Unknown"
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@app.post("/devices/", response_model=DeviceSchema)
def create_device(device: DeviceSchema, db: Session = Depends(get_db)):
    db_device = Device(
        device_id=device.device_id,
        user_id=device.user_id,
        device_type=device.device_type or "Unknown",
        device_name=device.device_name or "Unknown",
        start_date=device.start_date
    )
    db.add(db_device)
    db.commit()
    db.refresh(db_device)
    return db_device


@app.post("/glucose/", response_model=GlucoseReadingSchema)
def create_glucose_reading(reading: GlucoseReadingSchema, db: Session = Depends(get_db)):
    db_reading = GlucoseReading(
        reading_id=reading.reading_id,
        user_id=reading.user_id,
        timestamp=reading.timestamp or datetime.utcnow(),
        glucose_value=reading.glucose_value,
        source=reading.source or "Unknown"
    )
    db.add(db_reading)
    db.commit()
    db.refresh(db_reading)
    return db_reading


@app.post("/activity/", response_model=ActivityLogSchema)
def create_activity_log(log: ActivityLogSchema, db: Session = Depends(get_db)):
    db_log = ActivityLog(
        activity_id=log.activity_id,
        user_id=log.user_id,
        steps=log.steps,
        heart_rate=log.heart_rate,
        duration=log.duration,
        timestamp=log.timestamp or datetime.utcnow()
    )
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log

@app.post("/lab_result/", response_model=LabResultSchema)
def create_lab_result(lab: LabResultSchema, db: Session = Depends(get_db)):
    db_lab = LabResult(
        lab_id=lab.lab_id,
        user_id=lab.user_id,
        test_type=lab.test_type or "Unknown",
        value=lab.value,
        unit=lab.unit or "Unknown",
        date=lab.date or datetime.utcnow(),
        source=lab.source or "Unknown"
    )
    db.add(db_lab)
    db.commit()
    db.refresh(db_lab)
    return db_lab
