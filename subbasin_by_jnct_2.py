# %%
import geopandas as gpd
import pandas as pd

# Load your layers
polys = gpd.read_file(r"C:\Users\MBMcmanus\OneDrive - Garver\Documents\Work\Lawton\GIS\mapfile203_5070_with_allNearestAreas.geojson")     # has 'labels' field (list of strings)
points = gpd.read_file(r"C:\Users\MBMcmanus\OneDrive - Garver\Documents\Work\Lawton\GIS\junctions_412_export.shx.shp_4326.geojson")      # has 'name' field

# Make sure they use the same CRS
points = points.to_crs(polys.crs)

# Track assigned point names
assigned_point_names = set()

# %%
# Create a helper function
def get_nearest_available_point(polygon, label_list):
    # Get available matching points
    candidates = points[points['name'].isin(label_list) & ~points['name'].isin(assigned_point_names)].copy()
    if candidates.empty:
        return None
    # Compute distances
    candidates['distance'] = candidates.geometry.distance(polygon.geometry.centroid)
    # Find nearest
    nearest = candidates.loc[candidates['distance'].idxmin()]
    assigned_point_names.add(nearest['name'])
    return nearest['name']

# Make sure AreaMatches is a list (convert from string if needed)
def parse_matches(val):
    if isinstance(val, list):
        return val
    elif pd.isna(val):
        return []
    else:
        return [v.strip() for v in val.split(',') if v.strip()]

# Apply logic
polys['name'] = None  # or preserve existing 'name' values

for idx, row in polys.iterrows():
    if pd.notna(row.get('name')):
        # If name already exists, mark that point as used
        assigned_point_names.add(row['name'])
        continue

    label_list = parse_matches(row['AreaMatches'])
    if label_list:
        assigned = get_nearest_available_point(row, label_list)
        if assigned:
            polys.at[idx, 'name'] = assigned
# %%
# Save result
polys.to_file("subbasins_with_nearest_junction2.geojson", driver="GeoJSON")
polys

# %%
# count the number of polygons with a name
num_with_name = polys['name'].notnull().sum()
print(f"Number of polygons with a name: {num_with_name}")
# %%
# lets open a csv contiaing all the subbasin names, and use the polys gdf to get a list of all the named subbasins vs unnamed subbasins
csv_file_path = r"C:\Users\MBMcmanus\OneDrive - Garver\Documents\Work\Lawton\GIS\orig_subbasin_names_area.csv"
# open the csv with pandas
import pandas as pd
all_subbasins_df = pd.read_csv(csv_file_path)
all_subbasins_df

# %%
# add a column to all_subbasins_df called 'named' and set it to True if the subbasin name is in the polys gdf name column,
# and set it to False if the subbasin name is not in the polys gdf name column
all_subbasins_df['named'] = all_subbasins_df['Subbasin'].isin(polys['name'])
all_subbasins_df['named'] = all_subbasins_df['named'].astype(bool)
all_subbasins_df
# %%
# save the all_subbasins_df to a csv
all_subbasins_df.to_csv(r"C:\Users\MBMcmanus\OneDrive - Garver\Documents\Work\Lawton\GIS\orig_subbasin_names_area.csv", index=False)
# %%
