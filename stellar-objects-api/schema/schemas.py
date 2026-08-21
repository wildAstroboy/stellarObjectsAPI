def individual_serializer(star) -> dict:
    fields = {
        'id': str(star['_id']),
        'name': star['name'],
        'constellation': star['constellation'],
        'distance_light_years': star['distance_light_years'],
        'apparent_magnitude': star['apparent_magnitude'],
        'absolute_magnitude': star['absolute_magnitude'],
        'spectral_class': star['spectral_class'],
        'type': star['type'],
        'category': star['category'],
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