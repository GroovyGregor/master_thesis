'''Class for pattern radar data in 
`netCDF <https://www.unidata.ucar.edu/software/netcdf/>`_-format

'''
# Python modules 
from datetime import datetime
from netCDF4 import Dataset

# MasterModule
from .main_radar import Radar
from .radar_data import RadarData    

    
class PatternRadar(Radar):
    '''Class for Pattern radar data in `netCDF <https://www.unidata.ucar.edu/software/netcdf/>`_-format
    
    This class is designed for data coming from the 'Precipitation and 
    Attenuation Estimates from a High-Resolution Weather Radar Network' 
    (PATTERN) in 
    `netCDF <https://www.unidata.ucar.edu/software/netcdf/>`_-format. It 
    is a subclass of the more general :any:`Radar` class. Using this
    class, a PATTERN data file can be read in. 
    
    Attributes:
        name (:any:`str`): Name of operating institute. 'PaATTERN' in 
            this case.
        offset (:any:`int`): Angle, by which the pattern radar is 
            rotated.
        data (:any:`RadarData`): Used to save all kind of general radar 
            data and meta data.
        
    '''
    
    def __init__(self, radar_par):
        '''Initialization of object
        
        Saves attributes to the object and calls the 
        :any:`Radar.__init__`-method.
        
        Args:
            radar_par (dict): Radar parameters, e.g. name of file, 
                minute to be plotted, processing step, factor to 
                increase azimuth resolution, offset of radars azimuth 
                angle.
                
        '''
        # Call init method of super class
        super().__init__(radar_par)
        
        # Save attributes
        self.name = 'PATTERN'
        self.offset = radar_par['offset']
        
    def read_file(self, radar_par):
        '''Read in data
        
        Reads pattern radar data and saves data to object. Only 
        attributes needed for my calculations are read in. If more 
        information about the file and the attributes is wished, check 
        out the 
        `netCDF <https://www.unidata.ucar.edu/software/netcdf/>`_-file 
        with ncview or ncdump -h.
        
        Args:
            radar_par (dict): Radar parameters, e.g. name of file, 
                minute to be plotted, processing step, factor to 
                increase azimuth resolution, offset of radars azimuth 
                angle.
        '''
    
        # Define shorter names for input parameters
        proc_key = radar_par['proc_key']
        minute = radar_par['minute']
        
        # Create a RadarData object to generalize the radar properties
        radar_data = RadarData()
        
        # Open data file
        nc = Dataset(radar_par['file'], mode='r')

        # lon/lat coords of site
        radar_data.lon_site = nc.variables['lon'][:]                                        
        radar_data.lat_site = nc.variables['lat'][:]
        
        # Elevation of radar beam
        radar_data.ele = nc.variables['ele'][:]

        # Number of azimuth rays
        radar_data.azi_rays = nc.dimensions['azi'].size                                    
        
        # Number of range bins                                        
        radar_data.r_bins = nc.dimensions['range'].size 

        # Starting value of azimuth angle
        radar_data.azi_start = (
            (nc.variables['azi'][0] + self.offset + 360) % 360  
            )
        
        # Starting value of range
        radar_data.r_start = nc.variables['range'][0]
        
        # Azimuth angle steps between two measurements                                        
        radar_data.azi_steps = (
            (nc.variables['azi'][1] - nc.variables['azi'][0] + 360) 
            % 360
            )
          
        # Steps between 2 measurments in range
        radar_data.r_steps = (
            nc.variables['range'][1] - nc.variables['range'][0]
            )
                                         
        # Array of measured reflectivity                                        
        radar_data.refl = nc.variables[proc_key][:][int(minute*2)] 
       
        # Time at which radar scan started
        time_start = nc.variables['time_bnds'][int(minute*2)][0]
        radar_data.time_start = datetime.utcfromtimestamp(time_start)

        # Time at which radar scan ended
        time_end = nc.variables['time_bnds'][int(minute*2)][1]            
        radar_data.time_end = datetime.utcfromtimestamp(time_end)

        # Save the data to Pattern object
        self.data = radar_data
        

