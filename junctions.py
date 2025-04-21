# open a shapefile using geopandas and put it in a folium map
# %%
import geopandas as gpd
import folium
junction_file_path = r"C:\Users\MBMcmanus\OneDrive - Garver\Documents\Work\Lawton\GIS\junctions_412_export.shx.shp"
junctions = gpd.read_file(junction_file_path)
junctions
# %%
# check the crs of the junction gdf
print(junctions.crs)
# the crs seems to be wrong and is actually 26914, lets fix the crs and reproject to 4326
junctions.crs = "EPSG:26914"
junctions = junctions.to_crs(epsg=4326)
# %%
# lets reproject the junction gdf to 4326
junctions = junctions.to_crs(epsg=4326)
# %%
# create a folium map centered on the first junction
m = folium.Map(location=[junctions.geometry.y.mean(), junctions.geometry.x.mean()], zoom_start=12)
# add the junctions to the map
for _, row in junctions.iterrows():
    folium.Marker(location=[row.geometry.y, row.geometry.x], popup=row['junction']).add_to(m)
m
# %%
# output to a geojson file
output_path = junction_file_path.replace(".shx.shp", "")
output_path = junction_file_path+"_4326.geojson"
junctions.to_file(output_path, driver='GeoJSON')
# %%
# The HMS Basin file contains a list of subbasins, junctions, and reaches. 
# For each subbasin, it contains the downstream junction or reach.
# lets loop through the subbasins in the basin file for each subbasin, 
# if the downstream is a junction, add the subbasin name as a field to the junctions

# open the basin text file
basin_file_path = r"C:\Users\MBMcmanus\OneDrive - Garver\Documents\Work\Lawton\Ultimate_6_2_03 - updated 4.12\Ultimate_6_2_03.basin"
with open(basin_file_path, "r") as basin_file:
    basin_lines = basin_file.readlines()

"""
An example of the basin file snippet for a subbasin element is:
Subbasin: SQUAW C-2
     Last Modified Date: 15 April 2025
     Last Modified Time: 17:13:28
     Canvas X: 556173.086
     Canvas Y: 3828404.431
     Label X: 16.0
     Label Y: 0.0
     Area: 0.040
     Downstream: JR11570

     Discretization: None
     File: Ultimate_6_2_03.sqlite

     Canopy: None
     Allow Simultaneous Precip Et: No
     Plant Uptake Method: None

     Surface: None

     LossRate: Initial+Constant
     Percent Impervious Area: 0.0
     Initial Loss: 1.50
     Constant Loss Rate: 0.27

     Transform: Snyder
     Snyder Method: Standard
     Snyder Tp: 0.25
     Snyder Cp: 0.53

     Baseflow: Recession
     Recession Factor: 1
     Initial Baseflow: 0
     Threshold Flow: 0
End:
"""

# %%
# find each subbasin and its downstream element
subbasin_dict = {}
# basin_lines = iter(basin_lines)
b_file  = [s.strip('\n') for s in basin_lines]
basinList = []
line_start = 0
for i, v in enumerate(b_file):
    if (v == 'End:'):
        # print(i, v)
        # If not the beginning of the file, skip a blank line (+1) for the start of the subList.
        if len(basinList) > 0:
                basinList.append(b_file[line_start+1:i])
        else:
                basinList.append(b_file[line_start:i])
        line_start = i+1
        
# %%
# find basin description
for i, v in enumerate(basinList):
    if ('Subbasin: ') in v[0]:
        subbasinblock_index = i
        subbasin_name = v[0].split('Subbasin: ')[-1]
        # print(subbasin_name)
        # find the downstream element
        for subbasinblock_line in basinList[subbasinblock_index]:
            if 'Downstream: ' in subbasinblock_line:
                downstream_element = subbasinblock_line.split('Downstream: ')[-1]
                subbasin_dict[subbasin_name] = downstream_element
                print(subbasin_name,": ",downstream_element)
# for subbasinblock_line in basinList[subbasinblock_index]:
#     if 'Downstream: ' in subbasinblock_line:
#         downstream_element = subbasinblock_line.split('Downstream: ')[-1]
#         subbasin_dict[subbasin_name] = downstream_element

# %%
subbasin_dict

# %%
# lets reverse the subbasin_dict so that the downstream elements are the keys and the subbasins are the values
downstream_dict = {}
for subbasin, downstream in subbasin_dict.items():
    if downstream not in downstream_dict:
        downstream_dict[downstream] = [subbasin]
    else:
        downstream_dict[downstream].append(subbasin)
# if the value for a key is a list of length 1, change it to a string
for downstream, subbasins in downstream_dict.items():
    if len(subbasins) == 1:
        downstream_dict[downstream] = subbasins[0]
# %%
downstream_dict
# %%
# lets add the subbasin names to the junctions gdf as a new column called upstream_subbasin
junctions['upstream_subbasin'] = None
# loop through the junctions and add the subbasin names to the junctions gdf
for i, row in junctions.iterrows():
    # check if the junction name is in the downstream_dict
    if row['junction'] in downstream_dict:
        # if it is, add the subbasin name to the junctions gdf
        junctions.at[i, 'upstream_subbasin'] = downstream_dict[row['junction']]
    else:
        junctions.at[i, 'upstream_subbasin'] = None
junctions
# %%
# lets save the junctions gdf to a geojson again
junctions.to_file(output_path, driver='GeoJSON')
# %%
