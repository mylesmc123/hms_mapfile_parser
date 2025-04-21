# %%
import geopandas as gpd
from shapely.geometry import Point

# Load your polygon and point layers
polys = gpd.read_file(r"C:\Users\MBMcmanus\OneDrive - Garver\Documents\Work\Lawton\GIS\mapfile203_5070_with_allNearestAreas.geojson")     # has 'labels' field (list of strings)
points = gpd.read_file(r"C:\Users\MBMcmanus\OneDrive - Garver\Documents\Work\Lawton\GIS\junctions_412_export.shx.shp_4326.geojson")      # has 'name' field

# Make sure they use the same projection (important for distance calc)
points = points.to_crs(polys.crs)
# %%
polys
# %%
points
# %%
# Function to find nearest matching point
def get_nearest_matching_point_label(polygon, label_list):
    # Filter to only points whose name is in label_list
    matching_points = points[points['name'].isin(label_list)].copy()
    if matching_points.empty:
        return None
    # Compute distances
    matching_points['distance'] = matching_points.geometry.distance(polygon.geometry.centroid)
    # Get the closest one
    nearest = matching_points.loc[matching_points['distance'].idxmin()]
    return nearest['name']  # or nearest['id'] or whatever you want

# Apply to each polygon
polys['nearest_match'] = polys.apply(
    lambda row: get_nearest_matching_point_label(row, row['AreaMatches'].split(',')) if row['AreaMatches'] else None,
    axis=1
)

# %%
polys

# %%
# how many polygons have a nearest match
# count the number of polygons with a nearest match
num_with_match = polys['nearest_match'].notnull().sum()
print(f"Number of polygons with a nearest match: {num_with_match}")
# %%
# Save result
polys.to_file("subbasins_with_nearest_junction.geojson", driver="GeoJSON")

# %%
# For each polygon with no nearest match, find the nearest point in the entire points layer that is a candidate for a match by being in the 'AreaMatches' list
# and not already matched to another polygon.
# This is a bit more complex, as we need to ensure that the point we find is not already matched to another polygon.
# We can do this by filtering the points layer to only include points that are not already matched.
still_unmatched_polys = polys[polys['nearest_match'].isnull()]
still_unmatched_polys
# %%
def get_nearest_unmatched_point(still_unmatched_polygon, all_polygons):
    # Get the AreaMatches list for this polygon
    area_matches = still_unmatched_polygon['AreaMatches'].split(',')
    print (f"AreaMatches: {area_matches}")
    # Filter to only points whose name is in area_matches and not already matched
    # to not be matched, means a null value in the nearest_match column of the all_polygons gdf
    unmatched_basins = all_polygons[all_polygons['nearest_match'].isnull()]
    unmatched_points = points[points['name'].isin(area_matches) & points['name'].isin(unmatched_basins['nearest_match'])].copy()
    if unmatched_points.empty:
        return None
    # Compute distances
    unmatched_points['distance'] = unmatched_points.geometry.distance(polygon.geometry.centroid)
    # Get the closest one
    nearest = unmatched_points.loc[unmatched_points['distance'].idxmin()]
    return nearest['name']  # or nearest['id'] or whatever you want

# get the nearest unmatched point for each polygon and add it to the polys gdf
still_unmatched_polys['nearest_match'] = still_unmatched_polys.apply(
    lambda row: get_nearest_unmatched_point(row, polys) if row['AreaMatches'] else None,
    axis=1
)


# %%
# add the nearest match to the polys gdf
polys.update(still_unmatched_polys[['nearest_match']])

# %%
# count the number of polygons with a nearest match
num_with_match = polys['nearest_match'].notnull().sum()
print(f"Number of polygons with a nearest match: {num_with_match}")
# %%
