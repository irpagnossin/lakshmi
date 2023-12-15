from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class Base(BaseModel):
    created_at: datetime = datetime.utcnow()
    updated_at: Optional[datetime] = None
