import numpy as np
from copy import copy
from .extract_points import PointExtractor
from .color import Color #hex2lab, n_distinct

class ColorEncoding():
    # --------------------------------------------------------------------------
    def __init__(self, field='', _type='', colormap_type='',
                 domain=[], concepts=[], cardinality=1, constant=True,
                 redundant=False, mid_pos=-1):
        self.field         = field
        self._type         = _type
        self.colormap_type = colormap_type
        self.domain        = domain
        self._range        = [] # hexcolors
        self.mid_pos       = mid_pos # for diverging colormap
        self.concepts      = concepts
        self.cardinality   = cardinality
        self.hexcolors     = ['' for i in range(cardinality)]
        self.constant      = constant
        self.redundant     = redundant
        self.vegalite      = dict()
        self.points        = np.zeros((0,))
    # --------------------------------------------------------------------------
    def __str__(self):
        s = "field: {}\ntype: {}\nconcepts: {}".format(self.field, 
                                                       self._type,
                                                       self.concepts)
        return s
    # --------------------------------------------------------------------------
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return ((self.field, self._type, self.colormap_type, 
                     self.domain, self._range, self.concepts, 
                     self.constant) == 
                    (other.field, other._type, other.colormap_type, 
                     other.domain, other._range, other.concepts, 
                     other.constant))
        else:
            return False
    # --------------------------------------------------------------------------
    def __ne__(self, other):
        return not self.__eq__(other)
    # --------------------------------------------------------------------------
    def __hash__(self):
        return hash((tuple(self.concepts)))
    # --------------------------------------------------------------------------
    def __lt__(self, other):
        if self.field < other.field:
            return True
        else:
            return False
    # --------------------------------------------------------------------------
    def set_vegalite(self, color_encoding, reset=False):
        '''
        Set the color encoding in Vega-Lite specification
        '''
        if reset or self.constant: self.vegalite.clear()
        self.vegalite.update(color_encoding)
    # --------------------------------------------------------------------------
    def set_range(self, _range):
        '''
        Set the range of color scale
        '''
        self._range.clear()
        self._range = copy(_range)
    # --------------------------------------------------------------------------
    def gen_vegalite(self):
        '''
        Generate color encoding in Vega-Lite specification
        '''
        color_encoding = copy(self.vegalite)
        if self.constant:
            if self._range:
                color_encoding.update({'value': self._range[0]}) # steelblue
            else:
                color_encoding.update({'value': self._range})
            reset = True
        else:
            color_encoding.update({
                'field': self.field,
                'type': self._type,
                'scale': {
                    'domain': self.domain,
                    'range': self._range
                }
            })
            if self.redundant == True: color_encoding.update({"legend": False})
            if self.colormap_type == 'diverging' and self._type == 'quantitative':
                color_encoding['scale'].update({'interpolate': 'lab'})
        return color_encoding
    # --------------------------------------------------------------------------
    def extract_points(self, spec, data, mark, mark_obj):
        '''
        extract points [[x], [y], [label]] for calculating point distinctness
        '''
        if self.colormap_type != 'nominal': return list()
        attr_color = self.field
        if mark == 'bar':
            return PointExtractor.bar(spec, data, attr_color, self.concepts)
        elif mark == 'line' or mark == 'area':
            return PointExtractor.line(spec, data, attr_color)
        elif mark == 'circle':
            return PointExtractor.circle(spec, data, attr_color)
        elif mark == 'arc':
            return PointExtractor.arc(spec, data, attr_color, self.concepts, mark_obj)
    # --------------------------------------------------------------------------
    def gen_colormap(self):
        colormap_type = self.colormap_type
        hexcolors = self.hexcolors # for concepts

        if colormap_type == "constant":
            self.set_range(hexcolors)

        elif colormap_type == "nominal":
            reorder = [self.concepts.index(x) for x in self.domain]
            self.set_range(list(np.array(hexcolors)[reorder]))

        elif colormap_type == "sequential":
            cardinality = len(self.domain)
            mid_pos = self.mid_pos
            if mid_pos == -1:
                colors = Color.auto_gradient(hexcolors[0], cardinality)
            elif mid_pos == 0:
                start = "#cdcdcd"
                end = hexcolors[0]
                colors = np.concatenate([[start], 
                                          Color.auto_gradient(end, cardinality-1)]).tolist()
            elif mid_pos == (cardinality - 1):
                start = hexcolors[0]
                end = "#cdcdcd"
                colors = np.concatenate([Color.auto_gradient(start, cardinality-1)[::-1],
                                         [end]]).tolist()
            self.set_range(colors)

        elif colormap_type == "diverging":
            (start, end) = hexcolors
            cardinality = len(self.domain)
            even = True if cardinality%2 == 0 else False
            steps = int(np.floor(cardinality/2))
            if even:
                colors = np.concatenate([Color.auto_gradient(start, steps)[::-1], 
                                         Color.auto_gradient(end, steps)]).tolist()
            else:
                colors = np.concatenate([Color.auto_gradient(start, steps)[::-1], ["#cdcdcd"],
                                         Color.auto_gradient(end, steps)]).tolist()
            self.set_range(colors)
        return
    # --------------------------------------------------------------------------