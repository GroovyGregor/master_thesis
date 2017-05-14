'''Class for saving coordinates of cartesian grids'''

# python modules
import numpy as np


class GridCoordinates(object):
    '''Saves grid coordinates'''
    
    def __init__(self):
        '''Initialization of object
        
        Does nothing so far.
        
        '''
        pass
    
    @property
    def lat(self):
        '''Latitude coordinates
        
        Latitude coordinates of grid boxes of cartesian grid. 
        Must be a :any:`numpy.ndarray`.
        
        '''
        try:
            return self._lat
        except AttributeError:
            return 0
        
    @lat.setter
    def lat(self, new_lat):
        assert(
            isinstance(new_lat, np.ndarray)
            ), 'new_lat not a float'
        self._lat = new_lat
  
    @property
    def lon(self):
        '''Longitude coordinates
        
        Longitude coordinates of grid boxes of cartesian grid. 
        Must be a :any:`numpy.ndarray`.
        
        '''
        try:
            return self._lon
        except AttributeError:
            return 0
        
    @lon.setter
    def lon(self, new_lon):
        assert(
            isinstance(new_lon, np.ndarray)
            ), 'new_lon not a float'
        self._lon = new_lon
