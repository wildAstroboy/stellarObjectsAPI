def individual_serializer(star) -> dict:
    fields = {
        'id': str(star['_id']),
        'name': star['name'],
        'mass': star['mass'],
        'constellation': star['constellation'],
        'distance_light_years': star['distance_light_years'],
        'apparent_magnitude': star['apparent_magnitude'],
        'absolute_magnitude': star['absolute_magnitude'],
        'spectral_class': star['spectral_class'],
        'evolutionary_stage': star['evolutionary_stage'],
        'variable_type': star['variable_type'],
        'category': star['category'],
        'right_ascension': star['right_ascension'],
        'declination': star['declination'],
        'temperature_kelvin': star['temperature_kelvin'],
        'surface_gravity_log_g': star['surface_gravity_log_g'],
        'rotation': star['rotation'],
        'age_billion_years': star['age_billion_years'],
        'is_multi_star': star['is_multi_star'],
        'companion_stars': star['companion_stars'],
        'has_planets': star['has_planets'],
        'planet_count': star['planet_count'],
        'planet_names': star['planet_names'],
        'created_at': star.get('created_at'),
        'updated_at': star.get('updated_at')
    }

    # Remove any keys that have values of null
    cleaned_fields = {}

    for key, value in fields.items():
        if value is not None:
            cleaned_fields[key] = value

    return cleaned_fields

def list_serializer(star_list) -> list:

    return [individual_serializer(star) for star in star_list]

def individual_user_serializer(user) -> dict:

    username_key = next((k for k in user.keys() if k != '_id'), None)
    if not username_key:
        return None
    user_data = user[username_key]

    fields = {
        'username': user_data.get('username'),
        'full_name': user_data.get('full_name'),
        'email': user_data.get('email'),
        'hashed_password': user_data.get('hashed_password'),
        'disabled': user_data.get('disabled')
    }

    return fields
"""
def list_user_serializer(user_list) -> list:

    return [individual_user_serializer(user) for user in user_list]
"""