from typing import Optional, List
from pydantic import BaseModel, Field

class WaterPotabilityRequest(BaseModel):
    pH: float = Field(..., ge=0.0, le=14.0, description="pH level (BIS acceptable: 6.5 - 8.5)")
    Electrical_Conductivity: float = Field(..., ge=0.0, description="Electrical Conductivity in µS/cm at 25°C")
    TDS: Optional[float] = Field(None, ge=0.0, description="Total Dissolved Solids in mg/L (acceptable <= 500 mg/L). If null, computed as EC * 0.64")
    Total_Hardness: float = Field(..., ge=0.0, description="Total Hardness as CaCO3 in mg/L (acceptable <= 200 mg/L)")
    Calcium: float = Field(..., ge=0.0, description="Calcium ion concentration in mg/L (acceptable <= 75 mg/L)")
    Magnesium: float = Field(..., ge=0.0, description="Magnesium ion concentration in mg/L (acceptable <= 30 mg/L)")
    Chloride: float = Field(..., ge=0.0, description="Chloride ion concentration in mg/L (acceptable <= 250 mg/L)")
    Sulphate: float = Field(..., ge=0.0, description="Sulphate ion concentration in mg/L (acceptable <= 200 mg/L)")
    Iron: float = Field(..., ge=0.0, description="Dissolved iron concentration in mg/L (acceptable <= 1.0 mg/L)")
    Bicarbonate: float = Field(..., ge=0.0, description="Bicarbonate concentration in mg/L")
    Sodium: float = Field(..., ge=0.0, description="Sodium concentration in mg/L")

class ExceededParameter(BaseModel):
    parameter: str
    observed_value: float
    acceptable_limit: str
    description: str

class WaterPotabilityResponse(BaseModel):
    potability_code: int = Field(..., description="0 = Non-Potable, 1 = Potable")
    potability_label: str = Field(..., description="'Potable' or 'Non-Potable'")
    probability_potable: float = Field(..., ge=0.0, le=1.0, description="Model probability of compliance")
    probability_non_potable: float = Field(..., ge=0.0, le=1.0, description="Model probability of non-compliance")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Max class probability")
    standards_basis: str = "BIS IS 10500:2012 Drinking Water Specification"
    exceeded_parameters: List[ExceededParameter] = Field(default_factory=list)
    input_tds_calculated: bool = Field(False, description="True if TDS was derived from Electrical Conductivity via 0.64 factor")
    regulatory_advisory: str = (
        "Advisory: Model outputs reflect statistical classification against BIS IS 10500:2012 physicochemical limits. "
        "They do not replace comprehensive certified microbiological and toxicological laboratory testing."
    )
