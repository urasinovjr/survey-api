from enum import Enum

class Errors(Enum):
    """Enumeration for localized error messages."""
    MIN_VALUE = "Value must be >= {min}"
    MAX_VALUE = "Value must be <= {max}"
    INVALID_OPTION = "Invalid option"
    REQUIRED_DEPENDENCY = "Response for {depends_on} required"
    CONDITION_NOT_MET = "Question {number} requires {depends_on} {condition}"
    EXCEEDED_AREA = "Total area for {number} exceeds 2.1.4 ({total_area} m²)"
    INVALID_LIFT_CONFIG = "Invalid lift configuration for {floors} floors and {area} m² area"