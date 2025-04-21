# The objective of this repo was to provide scripts to assist in updating an old HMS model. The script helps to get a named subbasin feature layer that can be used with an Updated NLCD raster to update HMS parameters. 

There's 2 main files being used in this repo:
1. **mapFile_to_GeoJson.py** - This script takes a .map file from a 2003 model in HEC-HMS v2.2.1 and parses the coordinates in a feature layer. It will display the results in a map to help with identifying the correct projection. In this case, it was a model in Lawton, OK with a projection of EPSG:26914. We then project that to EPSG:4326 to view it in a folium webmap
  ![image](https://github.com/user-attachments/assets/52f0d27b-1c34-46c5-ac2c-af2b2657f19e)

The output geojson has to be cleaned up a bit, as it contains features for the model network as a feature on top of the subbasins. This cleanup was performed in QGIS.

2. **subbasin_by_jnct2.py** - This script uses the exported geojson from mapFile_to_GeoJson.py and a csv of the subbasins and areas extracted from the HEC-HMS v2.2.1 model which has been updated to v4.12 (Garver Location: "L:\2022\22W02330 - Lawton Stormwater MP\Design\Calculations\H&H\Hydrology\HEC-HMS_4.12\Ultimate_6_2_03 - updated 4.12"). Since the geojson was extracted from a mapfile, it has no naming for the subbasins, so this script uses the area of the geojson subbasins and tries to match the name from the CSV's subbasin areas. There are many duplicate areas found in the CSV, so there can be multiple matches of potential subbasin names which are added to the geojson as a list. The resulting output geojson was taken to QGIS and overlayed with the model schematic from the HMS 2.2.1 model, to see which of the candidate names was appropritate for each subbasin, and the name was updated accordingly. The image below illustrates how the Model schematic was overlayed on the subbasin geojson into QGIS.
   
   ![image](https://github.com/user-attachments/assets/5db77316-9ec8-40a5-82a4-17ec8b6d9d56)

# Final Output
The final output created in QGIS is the named subbasin geojson: **Subbasins_Named.geojson**

![image](https://github.com/user-attachments/assets/52894c64-b69a-4421-94ac-49d596ef46c8)

