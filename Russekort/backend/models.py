from pydantic import BaseModel
from typing import Optional, Dict, Any, List


class CardOut(BaseModel):
    id: str
    display_name: Optional[str] = None
    russ_title: Optional[str] = None
    line: Optional[str] = None
    quote: Optional[str] = None
    contact: Optional[Dict[str, Any]] = None
    bg_color: Optional[str] = None
    text_color: Optional[str] = None
    font: Optional[str] = None
    stickers: Optional[List[Dict[str, Any]]] = None
    image_url: Optional[str] = None
    created_at: Optional[str] = None
    scan_count: int


class TopItem(BaseModel):
    id: str
    display_name: Optional[str] = None
    scan_count: int
    image_url: Optional[str] = None

