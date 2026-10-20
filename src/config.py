"""Project-wide settings. Every other script imports from here."""

PROJECT_NAME = "SlopeSafe"

# Guwahati study area (city, hills, and the road toward Meghalaya)
STUDY_AREA = {
    "west": 91.55,
    "east": 91.95,
    "south": 26.05,
    "north": 26.30,
}

# Map centre: Guwahati
CENTER = (26.17, 91.75)

# Folium bounds format: [[south, west], [north, east]]
BOUNDS = [
    [STUDY_AREA["south"], STUDY_AREA["west"]],
    [STUDY_AREA["north"], STUDY_AREA["east"]],
]

# Coordinate reference systems
CRS_GEO = "EPSG:4326"      # lat/lon, used for web maps
CRS_METRIC = "EPSG:32646"  # UTM zone 46N, used for distance and area maths
