from uuid import UUID
from pydantic import BaseModel, field_validator, Field
from typing import List, Optional


class IdDTO(BaseModel):
    id: str = Field(..., alias="person__id")

    @field_validator('id', mode='before')
    def validate_uuid(cls, value):
        if isinstance(value, UUID):
            return str(value)
        return value


class PersonDTO(IdDTO):
    name: str = Field(..., alias="person__full_name")


class ActorDTO(PersonDTO):
    pass


class DirectorDTO(PersonDTO):
    pass


class WriterDTO(PersonDTO):
    pass


class FilmWorkModel(IdDTO):
    id: str
    title: str
    description: Optional[str]
    imdb_rating: Optional[float] = Field(..., alias="rating")
    genres: List[str]
    directors: List[DirectorDTO]
    actors: List[ActorDTO]
    writers: List[WriterDTO]
    directors_names: List[str]
    writers_names: List[str]
    actors_names: List[str]
