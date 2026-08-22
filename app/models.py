from sqlalchemy import Column, Integer, String
from .database import Base


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    roll_no = Column(String, unique=True, index=True)
    name = Column(String)
    parent_phone = Column(String)
    total_classes = Column(Integer, default=0)
    attended = Column(Integer, default=0)


class AttendanceRecord(Base):
    __tablename__ = "attendance_records"

    id = Column(Integer, primary_key=True, index=True)
    roll_no = Column(String, index=True)
    status = Column(String)

class WarningRequest(Base):
    __tablename__ = "warning_requests"

    id = Column(Integer, primary_key=True, index=True)
    roll_no = Column(String, index=True)
    status = Column(String, default="Pending")
    dispatched = Column(Integer, default=0)