from pydantic import BaseModel

# Declare body
class Star(BaseModel):
    name: str
    constellation: str
    distance_light_years: float
    apparent_magnitude: float
    absolute_magnitude: float
    spectral_class: str
    type: str
    category: str

    model_config = {
        "name": "Sun",
        "constellation": "None (Solar System)",
        "distance_light_years": 0.0000158,
        "apparent_magnitude": -26.74,
        "absolute_magnitude": 4.83,
        "spectral_class": "G2V",
        "type": "Main Sequence",
        "category": "Star"
    }