from pydantic import BaseModel
from typing import List, Optional

class Person(BaseModel):
    id: str
    name: str

class Relationship(BaseModel):
    source: str
    target: str
    type: str
    explanation: str
    provenance: str

class ExtractionResult(BaseModel):
    people: List[Person]
    relationships: List[Relationship]

class RescanRequest(BaseModel):
    pages: int = 2

class ArticleRequest(BaseModel):
    url: str

class DirectRelationship(BaseModel):
    type: str
    target_id: str
    explanation: str
    provenance: str

class PersonDetail(BaseModel):
    id: str
    name: str
    relationships: List[DirectRelationship]
