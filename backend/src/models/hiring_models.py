from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class ExperienceLevel(str, Enum):
    """Experience level enumeration."""
    ENTRY = "entry"
    JUNIOR = "junior"
    MID = "mid"
    SENIOR = "senior"
    LEAD = "lead"
    PRINCIPAL = "principal"
    STAFF = "staff"


class EmploymentType(str, Enum):
    """Employment type enumeration."""
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    CONTRACT = "contract"
    INTERNSHIP = "internship"
    TEMPORARY = "temporary"


class WorkLocation(str, Enum):
    """Work location type."""
    ONSITE = "onsite"
    REMOTE = "remote"
    HYBRID = "hybrid"


class HiringUrgency(str, Enum):
    """Hiring urgency level."""
    URGENT = "urgent"
    NORMAL = "normal"
    RELAXED = "relaxed"


class CompanySize(str, Enum):
    """Company size categories."""
    STARTUP = "startup"
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"
    ENTERPRISE = "enterprise"


class RoleDefinition(BaseModel):
    """Model for job role definition."""
    title: str = Field(..., description="Job title")
    department: str = Field(..., description="Department or team")
    experience_level: ExperienceLevel = Field(..., description="Required experience level")
    employment_type: EmploymentType = Field(default=EmploymentType.FULL_TIME)
    work_location: WorkLocation = Field(default=WorkLocation.HYBRID)
    
    # Core requirements
    responsibilities: List[str] = Field(..., description="Key responsibilities")
    required_skills: List[str] = Field(..., description="Required skills and qualifications")
    nice_to_have_skills: List[str] = Field(default_factory=list)
    
    # Additional details
    years_experience_min: int = Field(default=0, ge=0)
    years_experience_max: Optional[int] = Field(default=None, ge=0)
    education_requirements: Optional[str] = Field(default=None)
    certifications: List[str] = Field(default_factory=list)
    
    # Team and reporting
    team_size: Optional[int] = Field(default=None, ge=0)
    reports_to: Optional[str] = Field(default=None)
    direct_reports: Optional[int] = Field(default=0, ge=0)
    
    @validator('years_experience_max')
    def validate_experience_range(cls, v, values):
        if v is not None and 'years_experience_min' in values:
            if v < values['years_experience_min']:
                raise ValueError('Max experience must be greater than min experience')
        return v


class JobDescription(BaseModel):
    """Model for complete job description."""
    role_definition: RoleDefinition
    company_overview: str
    role_summary: str
    detailed_responsibilities: str
    requirements_section: str
    benefits: List[str]
    salary_range_min: Optional[int] = Field(default=None, ge=0)
    salary_range_max: Optional[int] = Field(default=None, ge=0)
    equity_offered: bool = Field(default=False)
    equity_details: Optional[str] = Field(default=None)
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    created_by: str = Field(default="system")
    
    @validator('salary_range_max')
    def validate_salary_range(cls, v, values):
        if v is not None and 'salary_range_min' in values and values['salary_range_min'] is not None:
            if v < values['salary_range_min']:
                raise ValueError('Max salary must be greater than min salary')
        return v


class InterviewStage(BaseModel):
    """Model for individual interview stage."""
    stage_name: str
    stage_type: str  # phone, technical, behavioral, panel, etc.
    duration_minutes: int = Field(ge=15, le=480)
    interviewers: List[str]
    focus_areas: List[str]
    sample_questions: List[str]
    evaluation_criteria: Dict[str, str]  # criterion -> description
    order: int = Field(ge=1)


class InterviewPlan(BaseModel):
    """Model for complete interview plan."""
    role_title: str
    total_stages: int = Field(ge=1, le=10)
    stages: List[InterviewStage]
    
    # Evaluation
    scorecard_template: Dict[str, Any]
    minimum_score_to_proceed: Optional[float] = Field(default=None, ge=0, le=100)
    
    # Timeline
    days_between_stages: int = Field(default=3, ge=1, le=14)
    total_estimated_days: int = Field(ge=1)
    
    # Special considerations
    technical_assessment_required: bool = Field(default=False)
    reference_check_required: bool = Field(default=True)
    background_check_required: bool = Field(default=True)
    
    @validator('stages')
    def validate_stages_count(cls, v, values):
        if 'total_stages' in values and len(v) != values['total_stages']:
            raise ValueError('Number of stages must match total_stages')
        return v


class HiringTimeline(BaseModel):
    """Model for hiring timeline."""
    start_date: datetime
    
    # Stage timelines
    job_posting_days: int = Field(default=3, ge=1)
    application_period_days: int = Field(default=14, ge=7)
    screening_days: int = Field(default=3, ge=1)
    interview_period_days: int = Field(default=21, ge=7)
    decision_days: int = Field(default=3, ge=1)
    offer_negotiation_days: int = Field(default=7, ge=3)
    
    # Calculated fields
    estimated_end_date: datetime
    total_days: int
    
    # Milestones
    milestones: List[Dict[str, Any]]
    
    # Factors
    urgency: HiringUrgency
    team_availability: str
    market_conditions: str


class SalaryBenchmark(BaseModel):
    """Model for salary benchmark data."""
    role_title: str
    location: str
    experience_level: ExperienceLevel
    company_size: CompanySize
    
    # Base salary
    base_salary_min: int = Field(ge=0)
    base_salary_median: int = Field(ge=0)
    base_salary_max: int = Field(ge=0)
    currency: str = Field(default="USD")
    
    # Additional compensation
    bonus_percentage_min: float = Field(default=0, ge=0, le=100)
    bonus_percentage_max: float = Field(default=0, ge=0, le=100)
    equity_percentage: Optional[str] = Field(default=None)
    equity_value_range: Optional[str] = Field(default=None)
    
    # Total compensation
    total_comp_min: int = Field(ge=0)
    total_comp_median: int = Field(ge=0)
    total_comp_max: int = Field(ge=0)
    
    # Market data
    data_source: str
    data_date: datetime
    sample_size: Optional[int] = Field(default=None, ge=1)
    market_demand: str  # high, medium, low
    
    # Percentiles
    percentile_25: Optional[int] = Field(default=None, ge=0)
    percentile_75: Optional[int] = Field(default=None, ge=0)
    percentile_90: Optional[int] = Field(default=None, ge=0)


class OfferLetter(BaseModel):
    """Model for offer letter."""
    # Candidate info
    candidate_name: str
    candidate_email: str
    candidate_address: Optional[str] = Field(default=None)
    
    # Position details
    position_title: str
    department: str
    reports_to: str
    start_date: datetime
    employment_type: EmploymentType
    work_location: WorkLocation
    
    # Compensation
    base_salary: int = Field(ge=0)
    bonus_target: Optional[int] = Field(default=None, ge=0)
    bonus_details: Optional[str] = Field(default=None)
    equity_offered: bool = Field(default=False)
    equity_details: Optional[str] = Field(default=None)
    
    # Benefits
    benefits_summary: List[str]
    pto_days: int = Field(default=0, ge=0)
    
    # Conditions
    contingencies: List[str]
    expiration_date: datetime
    
    # Metadata
    offer_date: datetime = Field(default_factory=datetime.now)
    prepared_by: str
    company_signatory: str


class HiringProfile(BaseModel):
    """Complete hiring profile containing all information."""
    session_id: str
    
    # Core components
    role_definition: Optional[RoleDefinition] = None
    job_description: Optional[JobDescription] = None
    interview_plan: Optional[InterviewPlan] = None
    timeline: Optional[HiringTimeline] = None
    salary_benchmark: Optional[SalaryBenchmark] = None
    offer_template: Optional[OfferLetter] = None
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    status: str = Field(default="draft")  # draft, active, completed, cancelled
    
    # Progress tracking
    completed_stages: List[str] = Field(default_factory=list)
    current_stage: Optional[str] = None
    
    # Notes and history
    notes: List[Dict[str, Any]] = Field(default_factory=list)
    revision_history: List[Dict[str, Any]] = Field(default_factory=list)
    
    def add_note(self, note: str, author: str = "system"):
        """Add a note to the profile."""
        self.notes.append({
            "note": note,
            "author": author,
            "timestamp": datetime.now().isoformat()
        })
        self.updated_at = datetime.now()
    
    def update_status(self, new_status: str):
        """Update profile status and track history."""
        old_status = self.status
        self.status = new_status
        self.revision_history.append({
            "change_type": "status_update",
            "old_value": old_status,
            "new_value": new_status,
            "timestamp": datetime.now().isoformat()
        })
        self.updated_at = datetime.now()