from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from decimal import Decimal


class UserSchema(BaseModel):
    user_id: int
    name: Optional[str] = None
    email: Optional[str] = None
    dob: Optional[datetime] = None
    gender: Optional[str] = None
    goal: Optional[str] = None

    class Config:
        from_attributes = True 


class DeviceSchema(BaseModel):
    device_id: int
    user_id: int
    device_type: Optional[str] = None
    device_name: Optional[str] = None
    start_date: Optional[datetime] = None

    class Config:
        from_attributes = True


class GlucoseReadingSchema(BaseModel):
    reading_id: int
    user_id: int
    timestamp: Optional[datetime] = None
    glucose_value: Optional[Decimal] = None
    source: Optional[str] = None

    class Config:
        from_attributes = True


class ActivityLogSchema(BaseModel):
    activity_id: int
    user_id: int
    steps: Optional[int] = None
    heart_rate: Optional[int] = None
    duration: Optional[int] = None
    timestamp: Optional[datetime] = None

    class Config:
        from_attributes = True


class MealLogSchema(BaseModel):
    meal_id: int
    user_id: int
    timestamp: Optional[datetime] = None
    meal_type: Optional[str] = None
    image_url: Optional[str] = None
    ai_food_label: Optional[str] = None
    estimated_calories: Optional[Decimal] = None

    class Config:
        from_attributes = True


class LabResultSchema(BaseModel):
    lab_id: int
    user_id: int
    test_type: Optional[str] = None
    value: Optional[Decimal] = None
    unit: Optional[str] = None
    date: Optional[datetime] = None
    source: Optional[str] = None

    class Config:
        from_attributes = True


class MoodLogSchema(BaseModel):
    mood_id: int
    user_id: int
    timestamp: Optional[datetime] = None
    mood_score: Optional[int] = None
    mood_note: Optional[str] = None

    class Config:
        from_attributes = True


class SleepLogSchema(BaseModel):
    sleep_id: int
    user_id: int
    date: Optional[datetime] = None
    duration: Optional[Decimal] = None
    quality_score: Optional[int] = None

    class Config:
        from_attributes = True


class BpReadingSchema(BaseModel):
    bp_id: int
    user_id: int
    timestamp: Optional[datetime] = None
    systolic: Optional[int] = None
    diastolic: Optional[int] = None
    device: Optional[str] = None

    class Config:
        from_attributes = True


class PaymentSchema(BaseModel):
    payment_id: int
    user_id: int
    timestamp: Optional[datetime] = None
    amount: Optional[Decimal] = None
    method: Optional[str] = None
    purpose: Optional[str] = None

    class Config:
        from_attributes = True
