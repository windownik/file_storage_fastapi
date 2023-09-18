
from pydantic import BaseModel


class File(BaseModel):
    file_id: int = 0
    file_type: str = '0'



