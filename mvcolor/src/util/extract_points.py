import numpy as np
from pandas import Categorical
import math

class PointExtractor():
    '''
    To calculate point distinctness, we extract data [x, y, label]
    for different mark types.
    '''
    # --------------------------------------------------------------------------
    zoom = 5
    # --------------------------------------------------------------------------
    @classmethod
    def bar(cls, spec, data, attr_color, concepts):
        '''
        Parameters
        ----------
        spec : dict
               Vega-Lite spec

        data : Dataframe
               the data using the visualization specification

        attr_color : str
                     the name of data attribute of the color encoding

        Results
        -------
        points : np.array([[x], [y], [label]]).T

        '''
        attr_x = spec['encoding']['x']['field']
        attr_y = spec['encoding']['y']['field']
        attr_col = ''
        attr_row = ''
        
        if 'column' in spec['encoding'].keys():
            attr_col = spec['encoding']['column']['field']
        if 'row' in spec['encoding'].keys():
            attr_row = spec['encoding']['row']['field']
            
        if not attr_col and not attr_row:
            # Simple bar chart
            if spec['encoding']['x']['type'] == 'nominal':
                # Vertical Bars
                if attr_x == attr_color: # redundant color encoding
                    data[attr_x] = Categorical(data[attr_x], categories=concepts)
                    data = data.sort_values(by=[attr_x])
                else:
                    data = data.sort_values(by=[attr_x], ascending=True)
                data_x = data[attr_x]
                data_y = data[attr_y]
                labels = data[attr_color]
                
                bar_width = cls.zoom/len(data_x)
                pos_x = np.array([(i+0.5)*bar_width for i in range(len(data_x))])
                
                y_min, y_max = data_y.min(), data_y.max()
                if 'scale' in spec['encoding']['y'].keys():
                    if 'domain' in spec['encoding']['y']['scale'].keys():
                        y_min, y_max = spec['encoding']['y']['scale']['domain']
                pos_y = 0.5 * cls.zoom * (data_y - y_min) / (y_max - y_min)
            
            elif spec['encoding']['y']['type'] == 'nominal':
                # Horizontal Bars
                if attr_y == attr_color: # redundant color encoding
                    data[attr_y] = Categorical(data[attr_y], categories=concepts)
                    data = data.sort_values(by=[attr_y])
                else:
                    data = data.sort_values(by=[attr_y], ascending=True)
                data_x = data[attr_x]
                data_y = data[attr_y]
                labels = data[attr_color]
                
                x_min, x_max = data_x.min(), data_x.max()
                if 'scale' in spec['encoding']['x'].keys():
                    if 'domain' in spec['encoding']['x']['scale'].keys():
                        x_min, x_max = spec['encoding']['x']['scale']['domain']
                pos_x = 0.5 * cls.zoom * (data_x - x_min) / (x_max - x_min)
                
                bar_height = cls.zoom/len(data_y)
                pos_y = np.array([(i+0.5)*bar_height for i in range(len(data_y))])[::-1]
                
        if attr_col and not attr_row:
            # Bar chart w/ column (Vertical Bars)
            data = data.sort_values(by=[attr_col, attr_x], ascending=True)
            data_x     = data[attr_x]
            data_y     = data[attr_y]
            data_col   = data[attr_col]
            labels     = data[attr_color]
            
            n_data = len(data)
            n_col  = len(data_col.unique())
            n_x    = len(data_x.unique())
            
            col_width, height = spec['width'], spec['height']
            bar_width = col_width / n_x
            bin_spacing = 20
            scaling = cls.zoom / ((col_width+bin_spacing) * n_data - bin_spacing)
            
            pos_x = scaling * np.array([i*(col_width+bin_spacing) + (j+0.5)* bar_width \
                              for i in range(n_col) for j in range(n_x)])
                
            y_min, y_max = data_y.min(), data_y.max()
            if 'scale' in spec['encoding']['y'].keys():
                if 'domain' in spec['encoding']['y']['scale'].keys():
                    y_min, y_max = spec['encoding']['y']['scale']['domain']
            pos_y = 0.5 * cls.zoom * (data_y - y_min) / (y_max - y_min)

        elif attr_row and not attr_col:
            # Bar chart w/ row (Horizontal Bars)
            data = data.sort_values(by=[attr_row, attr_y], ascending=True)
            data_x     = data[attr_x]
            data_y     = data[attr_y]
            data_row   = data[attr_row]
            labels     = data[attr_color]
            
            n_data = len(data)
            n_row  = len(data_row.unique())
            n_y    = len(data_y.unique())
            
            row_height, width = spec['height'], spec['width']
            bar_height = row_height / n_y
            bin_spacing = 20
            scaling = cls.zoom / ((row_height+bin_spacing) * n_data - bin_spacing)
            
            pos_y = scaling * np.array([i*(row_height+bin_spacing) + (j+0.5)* bar_height \
                              for i in range(n_row) for j in range(n_y)])
                
            x_min, x_max = data_x.min(), data_x.max()
            if 'scale' in spec['encoding']['x'].keys():
                if 'domain' in spec['encoding']['x']['scale'].keys():
                    y_min, y_max = spec['encoding']['x']['scale']['domain']
            pos_x = 0.5 * cls.zoom * (data_x - x_min) / (x_max - x_min)
        
        points = np.concatenate([[pos_x], [pos_y], [labels]], axis=0).T
        points = np.array([p for p in points if not np.any([math.isnan(v) \
                             for v in p if not isinstance(v, str)])])

        return points
    # --------------------------------------------------------------------------
    @classmethod
    def line(cls, spec, data, attr_color):
        '''
        Parameters
        ----------
        spec : dict
               Vega-Lite spec

        data : Dataframe
               the data using the visualization specification

        attr_color : str
                     the name of data attribute of the color encoding

        Results
        -------
        points : np.array([[x], [y], [label]]).T

        '''
        attr_x = spec['encoding']['x']['field']
        attr_y = spec['encoding']['y']['field']
        
        data.sort_values(by=[attr_color, attr_x], ascending=True)
        data_x = data[attr_x]
        data_y = data[attr_y]
        labels = data[attr_color]
            
        n_x = len(data_x.unique())
        n_label = len(labels.unique())
        spacing = cls.zoom/(n_x-1)
        
        pos_x = np.array([j*spacing for i in range(n_label) for j in range(n_x)])
        
        y_min, y_max = data_y.min(), data_y.max()
        if 'scale' in spec['encoding']['y'].keys():
            if 'domain' in spec['encoding']['y']['scale'].keys():
                y_min, y_max = spec['encoding']['y']['scale']['domain']
        pos_y = cls.zoom * (data_y - y_min) / (y_max - y_min)
       
        points = np.concatenate([[pos_x], [pos_y], [labels]], axis=0).T
        points = np.array([p for p in points if not np.any([math.isnan(v) \
                             for v in p if not isinstance(v, str)])])

        # sample extra points
        positions = points[:,:2].astype(float)
        labels = points[:,2]

        u_val, inv = np.unique(labels, return_inverse=True)

        for i, label in enumerate(u_val):
            positions_i = positions[np.where(inv == i)[0]]
            delta = np.diff(positions_i, axis=0) # delta x, delta y

            D = (np.sum((delta)**2, axis=1))**(0.5) # sqrt(((x2-x1)**2 + (y2-y1)**2))
            n_intervals = np.around(np.divide(D, 5))
            n_extra_points = n_intervals - 1
            n_extra_points[n_extra_points < 0] = 0
            
            n_intervals[n_intervals  == 0] = np.inf
            intervals = np.divide(delta, n_intervals[:, np.newaxis])
            
            for j, npoints in enumerate(n_extra_points):
                if npoints == 0: continue
                start_pos = positions_i[j]
                interval = intervals[j]
                extra_positions = np.array([start_pos + interval*(k+1) for k in range(int(npoints))])
                extra_points = np.concatenate((extra_positions.T, np.repeat(label, int(npoints))[:, np.newaxis].T))
                
                points = np.concatenate((points, extra_points.T))

        return points
    # --------------------------------------------------------------------------
    @classmethod
    def circle(cls, spec, data, attr_color):
        '''
        Parameters
        ----------
        spec : dict
               Vega-Lite spec

        data : Dataframe
               the data using the visualization specification

        attr_color : str
                     the name of data attribute of the color encoding

        Results
        -------
        points : np.array([[x], [y], [label]]).T

        '''
        attr_x = spec['encoding']['x']['field']
        attr_y = spec['encoding']['y']['field']
        
        data_x = data[attr_x]
        data_y = data[attr_y]
        labels = data[attr_color]
        
        x_min, x_max = data_x.min(), data_x.max()
        y_min, y_max = data_y.min(), data_y.max()
        if 'scale' in spec['encoding']['x'].keys():
            if 'domain' in spec['encoding']['x']['scale'].keys():
                x_min, x_max = spec['encoding']['x']['scale']['domain']
        if 'scale' in spec['encoding']['y'].keys():
            if 'domain' in spec['encoding']['y']['scale'].keys():
                y_min, y_max = spec['encoding']['y']['scale']['domain']
        pos_x = cls.zoom * (data_x - x_min) / (x_max - x_min)
        pos_y = cls.zoom * (data_y - y_min) / (y_max - y_min)
        
        return np.concatenate([[pos_x], [pos_y], [labels]], axis=0).T
    # --------------------------------------------------------------------------
    @classmethod
    def arc(cls, spec, data, attr_color, concepts, mark):
        '''
        Parameters
        ----------
        spec : dict
               Vega-Lite spec

        data : Dataframe
               the data using the visualization specification

        attr_color : str
                     the name of data attribute of the color encoding

        concepts : list
                   used to determine the positions of sorted parts

        Results
        -------
        points : np.array([[x], [y], [label]]).T

        '''
        attr_theta = spec['encoding']['theta']['field']
        
        # Calculate radius
        inner_radius = 0
        mid_radius   = 0.25 * cls.zoom
        outer_radius = 0.5 * cls.zoom
        if isinstance(mark, dict):
            if 'innerRadius' in mark.keys(): 
                inner_radius = mark['innerRadius']
            if 'outerRadius' in mark.keys(): # Resize
                inner_radius = 0.5 * cls.zoom * inner_radius / mark['outerRadius']
            mid_radius = (inner_radius + outer_radius) / 2
            
        # Calculate data position
        data_theta = data[attr_theta] # record accumulated theta position
        labels = data[attr_color]
        scaling = 2 * np.pi / data_theta.sum()
        accumulated_theta = 0
        start_pos_theta = np.zeros(shape=data_theta.shape)

        for i in range(len(data_theta)):
            _index = labels[labels == concepts[i]].index[0]
            start_pos_theta[i] = accumulated_theta
            accumulated_theta += data_theta[_index]

        start_pos_theta *= scaling
        
        # extract extra points
        delta = np.diff(np.concatenate((start_pos_theta, [2*np.pi]))) # interval between two different category
        n_intervals = np.around(np.divide(delta, np.pi*0.1))
        n_extra_points = n_intervals - 1
        n_extra_points[n_extra_points < 0] = 0
        n_intervals[n_intervals  == 0] = np.inf
        intervals = np.divide(delta, n_intervals)
        
        pos_theta = start_pos_theta.copy()
        extended_labels = labels.copy()
        for i, npoints in enumerate(n_extra_points):
            if npoints == 0: continue
            start = start_pos_theta[i]
            interval = intervals[i]
            extra_points = np.array([start + interval*(k+1) for k in range(int(npoints))])
            
            pos_theta = np.concatenate((pos_theta, extra_points))
            extended_labels = np.concatenate((extended_labels, np.repeat(concepts[i], int(npoints))))

        pos_x = 0.5 * cls.zoom + mid_radius * np.cos(pos_theta)
        pos_y = 0.5 * cls.zoom + mid_radius * np.sin(pos_theta)
            
        points = np.concatenate([[pos_x], [pos_y], [extended_labels]], axis=0).T
        return points
    # --------------------------------------------------------------------------