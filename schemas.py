from pydantic import BaseModel, Field


class EmployeeCreate(BaseModel):
    """Schema used for creating and updating an employee."""
    name: str       = Field(..., min_length=1, max_length=100, examples=["Alice Smith"])
    department: str = Field(..., min_length=1, max_length=100, examples=["Engineering"])
    salary: int     = Field(..., gt=0, examples=[75000])


class EmployeeOut(EmployeeCreate):
    """Schema returned from the API — includes the generated id."""
    id: int

    model_config = {"from_attributes": True}