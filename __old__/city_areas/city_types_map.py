city_types_names = {
    'tourist': 'Tourist City',
    'shopping': 'Leisure Shopping City',
    'nightlife': 'Nightlife City',
    'sport': 'Sport City',
    'cultural': 'Cultural City',
    'historic': 'Historic City',
    'business': 'Business City'
}

category_to_city_type = {
    'Monuments': {'tourist', 'cultural', 'historic'},
    'Museums & art galleries': {'tourist', 'cultural', 'historic'},
    'Cinemas & concert & theatres': {'tourist', 'nightlife', 'cultural', 'historic'},
    'Nightclubs & bars': {'business', 'nightlife', 'tourist'},
    'Cafés & restaurants': {'business', 'shopping', 'tourist'},
    'Shops & consumptive activies': {'business', 'sport', 'shopping', 'tourist'},
    'Offices & work premises': {'business', 'sport', 'tourist'},
    'Sport stadia & events': {'sport'},
    'Transport & mobility': {}
}