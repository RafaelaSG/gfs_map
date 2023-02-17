from siphon.catalog import TDSCatalog
from datetime import datetime
from xarray.backends import NetCDF4DataStore
import xarray as xr
import numpy as np
from netCDF4 import num2date
from metpy.units import units
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from metpy.plots import ctables


best_gfs = TDSCatalog('http://thredds.ucar.edu/thredds/catalog/grib/NCEP/GFS/'
                      'Global_0p25deg/catalog.xml?dataset=grib/NCEP/GFS/Global_0p25deg/Best')
print(best_gfs.datasets)
best_ds = list(best_gfs.datasets.values())[0]
ncss = best_ds.subset()
query = ncss.query()
ncss.variables

query.lonlat_box(north=2, south=-18, east=-30, west=-70).time(datetime.utcnow())
query.accept('netcdf4')
query.variables('Relative_humidity_height_above_ground')

data = ncss.get_data(query)
data = xr.open_dataset(NetCDF4DataStore(data))

print((data))
temp_3d = data['Relative_humidity_height_above_ground']
#Helper function for finding proper time variable
def find_time_var(var, time_basename='time'):
    for coord_name in var.coords:
        if coord_name.startswith(time_basename):
            return var.coords[coord_name]
    raise ValueError('No time variable found for ' + var.name)

time_1d = find_time_var(temp_3d)
lat_1d = data['latitude']
lon_1d = data['longitude']
time_1d

# Reduce the dimensions of the data and get as an array with units
temp_2d = temp_3d.metpy.unit_array.squeeze()

# Combine latitude and longitudes 
lon_2d, lat_2d = np.meshgrid(lon_1d, lat_1d)

# Create a new figure
fig = plt.figure(figsize=(15, 12))

# Add the map and set the extent
ax = plt.axes(projection=ccrs.PlateCarree())
#ax.set_extent([-100.03, -111.03, 35, 43])

# Retrieve the state boundaries using cFeature and add to plot
ax.add_feature(cfeature.STATES, edgecolor='gray')

# # Contour temperature at each lat/long
# contours = ax.contourf(lon_2d, lat_2d, temp_2d.to('degF'), 200, transform=ccrs.PlateCarree(),
#                        cmap='RdBu_r')
# Contour temperature at each lat/long
contours = ax.contourf(lon_2d, lat_2d, temp_2d, transform=ccrs.PlateCarree(),
                       cmap='RdBu')
#Plot a colorbar to show temperature and reduce the size of it
fig.colorbar(contours)

# Make a title with the time value
ax.set_title(f'RH forecast (%) for {time_1d[0].values}Z', fontsize=20)

# Plot markers for each lat/long to show grid points for 0.25 deg GFS
ax.plot(lon_2d.flatten(), lat_2d.flatten(), linestyle='none', marker='o',
        color='black', markersize=2, alpha=0.3, transform=ccrs.PlateCarree())
plt.show()
