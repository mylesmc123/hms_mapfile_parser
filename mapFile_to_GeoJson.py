# %% 
import geojson
from shapely.geometry import Polygon
from pyproj import Transformer
import re

# Sample input as multiline string (replace with file read if needed)
file_path = "mapfile.map"

# Read the file contents
with open(file_path, "r") as f:
    map_data = f.read()

# Step 1: Parse the map text into segments of coordinates
segments = []
current_segment = []

for line in map_data.splitlines():
    line = line.strip()
    if not line:
        continue
    if line.startswith("MapSegment:  closed"):
        if current_segment:
            segments.append(current_segment)
            current_segment = []
    elif re.match(r"^\d", line):  # Line with coordinates
        x_str, y_str = line.split(",")
        x = float(x_str.strip())
        y = float(y_str.strip())
        current_segment.append((x, y))

# Add last segment
if current_segment:
    segments.append(current_segment)

# Step 2: Transform coordinates from EPSG:32127 to WGS84
transformer = Transformer.from_crs("EPSG:26914", "EPSG:4326", always_xy=True)

features = []

for segment in segments:
    transformed = [transformer.transform(x, y) for x, y in segment]
    # Ensure polygon is closed
    if transformed[0] != transformed[-1]:
        transformed.append(transformed[0])
    polygon = geojson.Polygon([transformed])
    features.append(geojson.Feature(geometry=polygon))

# Step 3: Create FeatureCollection
feature_collection = geojson.FeatureCollection(features)

# Step 4: Save to GeoJSON file
output_path = file_path.replace(".map", ".geojson")
with open(output_path, "w") as f:
    geojson.dump(feature_collection, f, indent=2)

print(f"✅ GeoJSON saved to {output_path}")

# %%
# display the geojson file in a map
import folium
import json
from folium import GeoJson

# Load the GeoJSON file
with open(output_path) as f:
    geojson_data = json.load(f)
# Create a Folium map centered around the first coordinate of the first polygon
first_polygon = geojson_data['features'][0]['geometry']['coordinates'][0]
first_coord = first_polygon[0]
m = folium.Map(location=[first_coord[1], first_coord[0]], zoom_start=12)
# Add GeoJSON layer to the map
GeoJson(geojson_data).add_to(m)
# display the map
m
# %%
# export the geojson to shp
import geopandas as gpd
# convert the geojson to a geopandas dataframe
gdf = gpd.read_file(output_path)
# save the geopandas dataframe to a shapefile
output_shp_path = file_path.replace(".map", ".shp")
gdf.to_file(output_shp_path, driver='ESRI Shapefile')
print(f"✅ Shapefile saved to {output_shp_path}")


# %%
# count the number of polygons in the gdf
print(f"Number of polygons: {len(gdf)}")

# %%
# lets add an id to each polygon
gdf['id'] = gdf.index + 1
# now display the polygons in the folium map with the id as a label
m = folium.Map(location=[first_coord[1], first_coord[0]], zoom_start=12)
for _, row in gdf.iterrows():
    coords = row['geometry'].exterior.coords[:]
    folium.Polygon(locations=[(y, x) for x, y in coords], 
                   color='blue', 
                   fill=True, 
                   fill_opacity=0.5,
                   popup=f"ID: {row['id']}").add_to(m)
# display the map
m
# %%
# I also need to reproject a junction shpefile to overlap with the polygons
# lets load the junction shapefile
junction_file_path = r"C:\Users\MBMcmanus\OneDrive - Garver\Documents\Work\Lawton\GIS\junctions_412_export.shx.shp"
junction_gdf = gpd.read_file(junction_file_path)
# check the crs of the junction gdf
print(junction_gdf.crs)
# %%
# lets reproject the junction gdf to match the polygons
junction_gdf = junction_gdf.to_crs(gdf.crs)
# display the junction gdf on the map
junction_coords = junction_gdf.geometry.apply(lambda geom: geom.representative_point().coords[:]).tolist()
junction_coords = [coords[0] for coords in junction_coords]
# create a folium map with the junctions
m = folium.Map(location=[first_coord[1], first_coord[0]], zoom_start=12)
for _, row in gdf.iterrows():
    coords = row['geometry'].exterior.coords[:]
    folium.Polygon(locations=[(y, x) for x, y in coords], 
                   color='blue', 
                   fill=True, 
                   fill_opacity=0.5,
                   popup=f"ID: {row['id']}").add_to(m)
# add the junctions to the map
for coord in junction_coords:
    folium.Marker(location=[coord[1], coord[0]], 
                  icon=folium.Icon(color='red')).add_to(m)
# display the map with junctions
m
# %%