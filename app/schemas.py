from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class Skill(BaseModel):
    name: str = Field(min_length=1)
    source: str = Field(min_length=1)  # exact phrase from the posting


class JobPosting(BaseModel):
    title: str | None = None
    company: str | None = None
    modality: Literal["remote", "hybrid", "onsite"] | None = None
    location: str | None = None
    salary: str | None = None
    required_skills: list[Skill] = Field(default_factory=list)
    nice_to_have_skills: list[Skill] = Field(default_factory=list)


class ExtractRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    text: str = Field(min_length=1)