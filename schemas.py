
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class Education(BaseModel):
    model_config = ConfigDict(extra="forbid")

    institution: str | None = None
    degree: str | None = None
    field_of_study: str | None = None
    graduation_year: int | None = Field(default=None, ge=1950, le=2100)


class Experience(BaseModel):
    model_config = ConfigDict(extra="forbid")

    company: str | None = None
    role: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    description: list[str] = Field(default_factory=list)


class Project(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    description: str | None = None
    technologies: list[str] = Field(default_factory=list)


class Resume(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str | None = None
    email: EmailStr | None = None
    phone: str | None = None
    location: str | None = None
    summary: str | None = None

    skills: list[str] = Field(default_factory=list)
    education: list[Education] = Field(default_factory=list)
    experience: list[Experience] = Field(default_factory=list)
    projects: list[Project] = Field(default_factory=list)

    years_experience: float | None = Field(default=None, ge=0, le=80)
    certifications: list[str] = Field(default_factory=list)
    links: list[str] = Field(default_factory=list)
