"""Part 1 check: draw the Guwahati study area on a map.

Run from the project root:
    python src/check_boundary.py
Then open boundary_map.html in your browser.
"""
import folium
from config import BOUNDS, CENTER, STUDY_AREA


def main():
    m = folium.Map(location=CENTER, zoom_start=11, tiles=None)

    folium.TileLayer("OpenStreetMap", name="Street").add_to(m)
    folium.TileLayer(
        tiles=(
            "https://server.arcgisonline.com/ArcGIS/rest/services/"
            "World_Imagery/MapServer/tile/{z}/{y}/{x}"
        ),
        attr="Esri World Imagery",
        name="Satellite",
    ).add_to(m)
    folium.TileLayer("OpenTopoMap", name="Terrain").add_to(m)

    folium.Rectangle(
        bounds=BOUNDS,
        color="red",
        weight=2,
        fill=True,
        fill_opacity=0.05,
        tooltip="Study area",
    ).add_to(m)

    folium.Marker(CENTER, tooltip="Guwahati centre").add_to(m)
    folium.LayerControl().add_to(m)

    m.save("boundary_map.html")

    width_km = (STUDY_AREA["east"] - STUDY_AREA["west"]) * 111 * 0.9
    height_km = (STUDY_AREA["north"] - STUDY_AREA["south"]) * 111
    print("Saved boundary_map.html")
    print(f"Approx. size: {width_km:.0f} km x {height_km:.0f} km")


if __name__ == "__main__":
    main()
