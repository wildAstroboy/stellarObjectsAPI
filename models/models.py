from pydantic import BaseModel, Field
from typing import List, Optional


# Example
example = {
    'id': 1,
    'name': 'Sun',
    'mass': 1,
    'constellation': 'None (Solar System)',
    'distance_light_years': 0.0000158,
    'apparent_magnitude': -26.74,
    'absolute_magnitude': -0.17,
    'spectral_class': 'G2V',
    'evolutionary_stage': 'Main Sequence',
    'variable_type': 'None',
    'category': 'Star',
    'right_ascension': 'N/A (Solar System reference point)',
    'declination': 'N/A (Solar System reference point)',
    'temperature_kelvin': 5700,
    'surface_gravity_log_g': 4.4,
    'rotation': 'Not well constrained / estimated',
    'age_billion_years': 4.6,
    'is_multi_star': False,
    'companion_stars': [],
    'has_planets': True,
    'planet_count': 8,
    'planet_names':{
        "Mercury",
        "Venus",
        "Earth",
        "Mars",
        "Jupiter",
        "Saturn",
        "Uranus",
        "Neptune"
        }
    }


# Declare bodies
class Star(BaseModel):
    id: str | None = None
    name: str
    mass: float = Field(..., description='Mass in solar masses (M☉)')
    constellation: str
    distance_light_years: float
    apparent_magnitude: float
    absolute_magnitude: float
    spectral_class: str
    evolutionary_stage: str
    variable_type: str
    category: str
    right_ascension: str
    declination: str
    temperature_kelvin: int
    surface_gravity_log_g: float
    rotation: str
    age_billion_years: Optional[float] = None
    is_multi_star: bool
    companion_stars: List[str]
    has_planets: bool
    planet_count: int
    planet_names: List[str]