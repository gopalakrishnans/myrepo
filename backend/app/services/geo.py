import math


def zip_to_coords(zip_code: str) -> tuple[float, float] | None:
    import zipcodes
    matches = zipcodes.matching(zip_code)
    if not matches:
        return None
    z = matches[0]
    return (float(z["lat"]), float(z["long"]))


def haversine_miles(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 3958.8
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2) ** 2
    )
    return R * 2 * math.asin(math.sqrt(a))


def find_hospitals_near_zip(
    db,
    zip_code: str,
    radius_miles: int | None = None,
    procedure_id: int | None = None,
    limit: int = 20,
    offset: int = 0,
):
    from app.models.hospital import Hospital
    from app.models.price import Price

    coords = zip_to_coords(zip_code)
    if coords is None:
        raise ValueError(f"ZIP code not found: {zip_code}")

    origin_lat, origin_lon = coords

    query = db.query(Hospital)
    if procedure_id is not None:
        query = query.join(Price).filter(Price.procedure_id == procedure_id)
        query = query.distinct()

    hospitals = query.all()

    results = []
    for h in hospitals:
        if h.latitude is None or h.longitude is None:
            continue
        dist = haversine_miles(origin_lat, origin_lon, h.latitude, h.longitude)
        if radius_miles is not None and dist > radius_miles:
            continue
        results.append((h, round(dist, 1)))

    results.sort(key=lambda x: x[1])
    total = len(results)
    page = results[offset : offset + limit]

    return page, total
