###program that plots differences between two radar imgaes on a new grid

'''
program plots differences between two radar images after interpolating
to the same cartesian grid.
'''





########################################################################
### modules ###
########################################################################

#modules
import matplotlib.pyplot as plt
import numpy as np
import re
import seaborn as sb
import parameters as par
from pathlib import Path
from MasterModule.MainRadar import Radar
from MasterModule.DWDRadar import Dwd
from MasterModule.PatternRadar import Pattern
from MasterModule.RadarData import RadarData
from MasterModule.CartesianGrid import CartesianGrid
from MasterModule.GridParameter import GridParameter





########################################################################
### lists, parameters ###
########################################################################

'''
Some parameters, that can be set in parameters.py.
Also, lists of program are defined here.
'''

#parameters
file1     = par.radar1[0] #name of first radar data file
file2     = par.radar2[0] #name of second radar data file
minute1   = par.radar1[1] #minute of 1st data file to be plotted
minute2   = par.radar2[1] #minute of 2nd data file to be plotted
proc_key1 = par.radar1[2] #key for proc. step of 1st radar
proc_key2 = par.radar2[2] #key for proc. step of 2nd radar
res_fac1  = par.radar1[3] #factor to incr. azi. res. of 1st radar
res_fac2  = par.radar2[3] #factor to incr. azi. res. of 2nd radar

#grid_par = [[[lon_start,lon_end],[lat_start,lat_end],
#          [lon_site,lat_site],max_range,resolution]]
grid_par  = par.grid_par  #numpy array containing grid parameters 
tick_frac = par.tick_frac #fract. of grid lines to be labeled in plots

#lists
l_refl    = []            #reflectivity matrices of radars
l_xlabel  = []            #for labeling x-axis
l_ylabel  = []            #for labling y-axis





########################################################################
### Create Radar objectives ###
########################################################################

'''
For both radars, a radar objective is created. The file name contains
information about the type of radar (dwd or pattern) and in case of
the pattern radar, also about the processing step (level1, level2).
--> scan file_name to get radar and processing step, then create the
correct radar objective (dwd or pattern object)
'''

### 1st radar ###
#pattern radar, proc. step: 'level1'
if re.search('level1',file1):         
    radar1 = Pattern('dbz',minute1,file1,res_fac1)
#pattern radar, proc. step: 'level2'      
elif re.search('level2', file1):     
    radar1 = Pattern(proc_key1,minute1,file1,res_fac1) 
#dwd radar
elif re.search('dwd_rad_boo', file1): 
    radar1 = Dwd(file1,res_fac1)



### 2nd radar ###
#same procedure as for level1
if re.search('level1',file2):
    radar2 = Pattern('dbz',minute2,file2,res_fac2)  
elif re.search('level2', file2):
    radar2 = Pattern(proc_key2,minute2,file2,res_fac2)
elif re.search('dwd_rad_boo', file2):
    radar2 = Dwd(file2,res_fac2)



#create list of both radar objectives, for easy looping
radars = [radar1,radar2]






########################################################################
### Create new cartesian grid ###
########################################################################
    
'''
Creates the cartesian grid, on which data shall be plotted.
'''

#CartesianGrid-object
car_grid = CartesianGrid(grid_par) 
    
   
   
   
    
########################################################################
### Main Loop ###
########################################################################

'''
A lot of calculations are the same for both radars. These common
calculations are done in this main loop.
'''

###loop through both radars
for radar in radars:
    
        
    ####################################################################
    ### read in data ###
    ####################################################################
    
    '''
    Data is saved to a Radar-Object. The method used to read in the data
    differs, depending on the radar that shall be plotted. 
    '''

    #read in data
    radar.read_file()
    
    
    
    
    
    ####################################################################
    ### artificially increase azimuth resolution ###
    ####################################################################
    
    '''
    The azimuth resolution of the radar usually is 1°. To avoid 
    empty grid boxes in the new cartesian grid, the azimuth 
    resolution can be increased artificially. Each gridbox will 
    be divided into 'x' gridboxes with the same value (x beeing the 
    res_factor). This is done by duplicating all lines (azimuths) 
    'x'-times.  This is equivalent to dividing all grid boxes at this
    azimuth into 'x' sub-grid boxes, when the coordinates of the 
    sub grid boxes are adjusted (growing with 1/x ° instead of 1°).
    '''
    
    #artificially increase azimuth resolution
    radar.increase_azi_res()
    
    
    
    
    
    ####################################################################
    ### calculate coordinates of middle pixel for each box ###
    ####################################################################
    
    '''
    Coordinates of data are given at specific points, but are
    valid for a box. The coordinates of the data points are given
    at the far edge in range and near edge in azimuth for each
    grid box (looking from radar site).
    This method calculates for each grid box the polar coordinates 
    of the middle pixel out of the given coordinates at the edge of
    the box.
    The middle pixel is calculated through averaging of two 
    consecutive ranges and through averaging of two consecutive 
    azimuth angles.
    '''
        
    #pixel_center is a np.meshgrid 
    #pixel_center[0] = range, pixel_center[1] = azi.
    pixel_center = radar.get_pixel_center() 
    
    
    
    
    
    ####################################################################
    ### transform polar coordinates to lon/lat ###
    ####################################################################
    
    '''
    Transformation of polar coordinates of grid boxes (middle pixel) to 
    cartesian coordinates, using a wradlib function
    '''
    
    #get cartesian coordinates of radar data
    lon, lat = radar.polar_to_cartesian(pixel_center[0],pixel_center[1])
    
    
    
    
    
    ####################################################################
    ### rotated pole transformation ###
    ####################################################################
    
    '''
    Transform the cartesian coordinates to rotated pole coordinates using
    a function from Claire Merker.
    '''
    
    #coords_rot.shape=(360,600,3), (azi,range,[lon,lat,height])
    coords_rot = radar.rotate_pole(lon,lat) 

    #save rotated coords to radar object
    radar.data.lon_rota = coords_rot[:,:,0]
    radar.data.lat_rota = coords_rot[:,:,1]
     
    
    
    
      
    ####################################################################
    ### Interpolate radar data to cartesian grid ###
    ####################################################################
    
    '''
    Interpolates radar data to the new cartesian grid, by averaging all
    data points falling into the same grid box of the new 
    cartesian grid. 
    Due to noise and dbz beeing a logarithmic unit, 'no rain' can have a 
    large spread in dbz units. --> Reflectiviy smaller than 5 dbz, 
    will be set to 5,to avoid having large differences at low 
    reflectivity.
    '''
    
    #interpolate reflectivity to the new grid
    refl           = car_grid.data2grid(radar)
    
    #set reflectivities smaller than 5 to 5
    refl[refl < 5] = 5
    
    #append inverted reflectivity matrix to list
    #mirror columns --> matplotlib plots the data exactly mirrored
    l_refl.append(refl[::-1])
    




########################################################################
### Calculate Difference ###
########################################################################

'''
Calculates differences of the two reflectivity matrices.
'''

#difference between two data fields
refl_diff = l_refl[1] - l_refl[0]





########################################################################
### prepare plot ###
########################################################################

'''
prepares plot by defining labling lists etc. 
'''

#calculates rotated lon coord of each grid cell of the cartesian grid
lon_plot = np.arange(
                     car_grid.par.lon_start,
                     car_grid.par.lon_end,
                     car_grid.par.res_deg
                     )
                     
#calculates rotated lat coord of each grid cell of the cartesian grid                        
lat_plot = np.arange(
                     car_grid.par.lat_start,
                     car_grid.par.lat_end,
                     car_grid.par.res_deg
                     )

#number of grid lines to be plotted
ticks    = int(\
               np.ceil(\
               (car_grid.par.lon_end - car_grid.par.lon_start)\
               /car_grid.par.res_deg)\
               )

#fill label list with lon/lat coordinates to be labeled
for i in range(0,ticks,int(ticks/tick_frac)):
    l_xlabel.append(round(lon_plot[i],2))
    l_ylabel.append(round(lat_plot[i],2))





########################################################################
### actual plot ###
########################################################################

'''
Plots difference matrix on the new cartesian grid using seaborn.
'''

#create subplot
fig,ax = plt.subplots() 

#create heatmap                                                                                                              
sb.heatmap(refl_diff,vmin = -70, vmax = 70,cmap = 'bwr')                  

#x- and y-tick positions
ax.set_xticks(np.arange(0,ticks,ticks/tick_frac), minor = False)                
ax.set_yticks(np.arange(0,ticks,ticks/tick_frac), minor = False)                

#x- and y-tick labels
ax.set_xticklabels(l_xlabel,fontsize = 14)                                        
ax.set_yticklabels(l_ylabel,fontsize = 14)                                        

#grid
ax.xaxis.grid(True, which='major',color = 'k')                                
ax.yaxis.grid(True, which='major',color = 'k')

#put grid in front of data                        
ax.set_axisbelow(False)  

#label x- and y-axis                                                  
plt.xlabel('longitude',fontsize = 16)                                    
plt.ylabel('latitude', fontsize = 16)    

#title                           
plt.title(\
          'Difference plot at '\
          +str(radar.data.time_start),
          fontsize = 20
          )  

#show  
plt.show()                                                                

