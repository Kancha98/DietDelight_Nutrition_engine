from database import Base, engine
from models import FutureLabInput

Base.metadata.create_all(bind=engine)
print("✅ future_lab_inputs table created")