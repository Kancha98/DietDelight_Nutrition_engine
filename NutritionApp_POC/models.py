from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class User(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, default="Unknown")
    email = Column(String, default="Unknown")
    dob = Column(DateTime, default="Unknown")
    gender = Column(String, default="Unknown")
    goal = Column(String, default="Unknown")


class Device(Base):
    __tablename__ = "devices"
    device_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    device_type = Column(String, default="Unknown")  # Fitbit, Libre3, etc..
    device_name = Column(String, default="Unknown")
    start_date = Column(DateTime, default="Unknown")


class GlucoseReading(Base):
    __tablename__ = "glucose_readings"
    reading_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    timestamp = Column(DateTime, default=datetime.utcnow)
    glucose_value = Column(Float, nullable=True)
    source = Column(String, default="Unknown")


class ActivityLog(Base):
    __tablename__ = "activity_logs"
    activity_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    steps = Column(Integer, default="Unknown")
    heart_rate = Column(Integer, default="Unknown")
    duration = Column(Integer, default="Unknown")
    timestamp = Column(DateTime, default=datetime.utcnow)


class MealLog(Base):
    __tablename__ = "meal_logs"
    meal_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    timestamp = Column(DateTime, default=datetime.utcnow)
    meal_type = Column(String, default="Unknown")
    image_url = Column(String, default="Unknown")
    ai_food_label = Column(String, default="Unknown")
    estimated_calories = Column(Float, nullable=True)


class LabResult(Base):
    __tablename__ = "lab_results"
    lab_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    test_type = Column(String, default="Unknown")
    value = Column(Float, nullable=True)
    unit = Column(String, default="Unknown")
    date = Column(DateTime, default="Unknown")
    source = Column(String, default="Unknown")


class FutureLabInput(Base):
    __tablename__ = "future_lab_inputs"

    id = Column(Integer, primary_key=True, index=True)
    source = Column(String, default="manual")
    condition_supported = Column(String, default="unknown")
    test_type = Column(String, nullable=False)
    format = Column(String, default="unknown")
    validation = Column(String, default="unknown")
    unit = Column(String, default="unknown")
    database_field_name = Column(String, default="unknown")


class MoodLog(Base):
    __tablename__ = "mood_logs"
    mood_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    timestamp = Column(DateTime, default=datetime.utcnow)
    mood_score = Column(Integer, default="Unknown")
    mood_note = Column(String, default="Unknown")


class SleepLog(Base):
    __tablename__ = "Sleep_logs"
    sleep_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    date = Column(DateTime, default="Unknown")
    duration = Column(Float, nullable=True)
    quality_score = Column(Integer, default="Unknown")


class BpReading(Base):
    __tablename__ = "bp_readings"
    bp_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    timestamp = Column(DateTime, default=datetime.utcnow)
    systolic = Column(Integer, default="Unknown")
    diastolic = Column(Integer, default="Unknown")
    device = Column(String, default="Unknown")


class Payment(Base):
    __tablename__ = "payments"
    payment_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    timestamp = Column(DateTime, default=datetime.utcnow)
    amount = Column(Float, nullable=True)
    method = Column(String, default="Unknown")
    purpose = Column(String, default="Unknown")
