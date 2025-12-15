# import enum
# from datetime import datetime, timezone
# from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class SchedulesTable(SQLModel, table=True):
    __tablename__="schedules_table"
    
    # Fields
    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        title="Job Id",
        description="Unique identifier for the scheduled job",
    )