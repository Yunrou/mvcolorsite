import os, json
import numpy as np
from pandas import DataFrame
from copy import copy, deepcopy

import altair as alt
from altair_saver import save

from django.conf import settings
url = os.path.join(settings.MEDIA_ROOT, 'screenshot')

from .util.color_encoding import ColorEncoding
# ==============================================================================
class View():
    # --------------------------------------------------------------------------
    def __init__(self, name: str, title: str, spec: dict, data: DataFrame, config: dict):
        self.name = name
        self.title = title
        self.content = ''
        self.spec = spec
        self.data = data
        self.config = config
        self.mark = ''
        self.color_encoding = ColorEncoding()
        self.order_encoding = {}
        self.transform = []
        self.concept_sets = []
        self.color_encodings = []
        self.vegalite_parser(spec)
    # --------------------------------------------------------------------------
    def __str__(self):
        s = "name: {}\nmark: {}\ncolor encoding: {}".format(self.name,
                                                            self.mark,
                                                            self.color_encoding)
        return s
    # --------------------------------------------------------------------------
    def vegalite_parser(self, spec: dict) -> list:
        '''
        Extract encoding informations, and set mark and set suggested color encodings

        Parameters
        ----------
        obj : dict
              The spec by grammar of vegalite

        '''
        if 'layer' not in spec.keys():
            mark = spec['mark']
            mark_obj = mark
            if isinstance(mark, dict):
                self.mark = self.extract_value(mark, 'type')[0]
            elif isinstance(mark, str):
                self.mark = mark  
        else:
            for layer in spec['layer']:
                mark = layer['mark']
                if isinstance(mark, dict):
                    mark_type = self.extract_value(mark, 'type')[0]
                    if mark_type == 'text': continue
                    self.mark = mark_type
                elif isinstance(mark, str):
                    if mark == 'text': continue
                    self.mark = mark
                mark_obj = mark

        encodings = spec['encoding']
        self.concept_sets = self.extract_concept_sets(self.mark, self.data, encodings)
        
        for i, ce in enumerate(self.color_encodings):
            if self.mark not in ('bar', 'line', 'area', 'circle', 'arc'):
                continue
            ce.points = ce.extract_points(self.spec, 
                                          self.data, 
                                          self.mark,
                                          mark_obj)

        return
    # --------------------------------------------------------------------------
    def extract_concept_sets(self, mark, data, encoding: dict):
        '''
        For one chart, analyze its encoding channels, and return a list of a 
        must need data field and suggested data fields to be encoded, so that
        we can overwrite the color channel information for recoloring.

        Parameters
        ----------
        data : DataFrame

        encoding : dict

        Results
        -------
        concept_sets : list
        '''
        color_encodings = []
        # channel: x,y,color,size,etc; info: its value
        fields = [info['field'] for channel, info in encoding.items() \
                    if ('field' in info.keys()) and channel != 'order']
        self.content = ' '.join(set(fields))
        # Whether user has defined a order for a data attribute
        has_order = False
        if 'order' in encoding.keys():
            ascending = True
            if 'sort' in encoding['order'].keys():
                if encoding['order']['sort'] == 'descending':
                    ascending = False
            data = data.sort_values(by=[encoding['order']['field']], ascending=ascending)
            has_order = True

        # Record fields
        for channel, info in encoding.items():
            if channel == "order": continue
            # no field, e.g. color -> value -> red
            if 'field' not in info.keys():
                continue

            data_field    = info['field']
            data_type     = info['type']
            colormap_type = ''
            domain        = []
            concepts      = []
            mid_pos       = -1

            if data_type == 'nominal':
                colormap_type = 'nominal'
                if has_order:
                    domain = list(data[data_field].unique())
                elif 'sort' in info.keys():
                    ascending = True
                    if 'order' in info['sort']:
                        ascending = False if info['sort']['order'] \
                                    == 'descending' else True
                    if 'field' in info['sort']:
                        by_field = info['sort']['field']
                        if by_field:
                            sorted_data = data.sort_values(by=[by_field], 
                                                           ascending=ascending)
                            domain = list(data[data_field].unique())
                        else: domain = sorted(list(data[data_field].unique()))
                    else: domain = sorted(list(data[data_field].unique()))
                elif 'scale' in info.keys():
                    if 'domain' in info['scale'].keys():
                        domain = info['scale']['domain']
                else:
                    domain = sorted(list(data[data_field].unique()))
                concepts = list(map(str, deepcopy(domain)))
                if 'scale' in info.keys(): 
                    # set the color legend order if user specified
                    if 'domain' in info['scale'].keys():
                        domain = info['scale']['domain']

            elif data_type == 'ordinal':
                if 'scale' in info.keys():
                    if 'domain' in info['scale'].keys():
                        domain = info['scale']['domain']
                    else:
                        domain = sorted(list(data[data_field].unique()))
                    if 'range' in info['scale'].keys():
                        _range = info['scale']['range']

                        if '#f2f0ec' in _range:
                            mid_pos = _range.index('#f2f0ec')
                            if mid_pos == 0 or (mid_pos == (len(_range)-1)):
                                colormap_type = 'sequential'
                                concepts = [data_field]
                            else:
                                colormap_type = 'diverging'
                                concepts = [domain[0], domain[-1]]

                if not concepts:
                    colormap_type = 'sequential'
                    domain = sorted(list(data[data_field].unique()))
                    concepts = [data_field]

            elif data_type in ['quantitative']:
                domain = [data[data_field].min(), data[data_field].max()]
                if domain[0] < 0 and domain[1] > 0:
                    colormap_type = 'diverging'
                    concepts = ['low-'+data_field, 'high-'+data_field]
                else:
                    colormap_type = 'sequential'
                    concepts = [data_field]
            else:
                continue

            if len(concepts) > 10: continue
            # Create a ColorEncoding object
            color_encoding = ColorEncoding(field=data_field,
                                           _type=data_type, 
                                           colormap_type=colormap_type,
                                           domain=domain, 
                                           concepts=concepts,
                                           mid_pos=mid_pos,
                                           cardinality=len(concepts),
                                           constant=False,
                                           redundant=True)

            if channel == 'color':
                self.color_encoding.set_vegalite(deepcopy(info), reset=False)
                color_encoding.set_vegalite(deepcopy(info), reset=False)

                # if not (fields.count(data_field) > 1): 
                    # non-redundant color encoding
                concept_sets = [set(concepts)]
                color_encoding.redundant = False
                self.color_encodings = [color_encoding]
                return concept_sets
                # else: # redundant
                #     color_encodings.append(color_encoding)

            else:
                if data_type in ['nominal']:
                    # other channel's encoding
                    if channel in ['row', 'column'] or mark == 'bar':
                        color_encodings.append(color_encoding)

        # reduce the one redundancy and set self.color_encodings
        color_encodings = list(set(color_encodings))

        # Extract concept set from title for constant color encoding
        color_encodings.insert(0, ColorEncoding(colormap_type='constant',
                                                field='constant',
                                                concepts=[self.title],
                                                cardinality=1,
                                                constant=True, 
                                                redundant=True))
        self.color_encodings = color_encodings

        concept_sets = [set(ce.concepts) for ce in color_encodings]

        return concept_sets
    # --------------------------------------------------------------------------
    def extract_value(self, obj: dict, key: str) -> list:
        '''
        Extract values of a specific key in a nested dictionary.
        '''
        values = []

        def extract(obj):
            if isinstance(obj, dict):
                # tear down dictionary
                for k, v in obj.items():
                    if k == key:
                        values.append(v)    
                    if isinstance(v, (dict, list)):
                        extract(v)

            elif isinstance(obj, list):
                # tear down list
                for e in obj:
                    if isinstance(e, (dict, list)):
                        extract(e)
        extract(obj)

        return values
    # --------------------------------------------------------------------------
    def set_order_encoding(self, order_encoding, reset=False):
        if reset: self.order_encoding.clear()
        self.order_encoding.update(order_encoding)
    # --------------------------------------------------------------------------
    def set_transform(self, transform):
        # if reset: self.transform.clear()
        # usually for choropleth maps
        self.transform = transform
    # --------------------------------------------------------------------------
    def find_color_encoding(self, concept_set):
        '''
        Given the concept set, find out it corresponds to which color encoding
        for colormap generation
        '''
        idx = self.concept_sets.index(concept_set)
        return self.color_encodings[idx]
    # --------------------------------------------------------------------------
    def set_color_encoding(self, color_encoding):
        self.color_encoding = color_encoding    
    # --------------------------------------------------------------------------
    def recolor(self):
        spec = copy(self.spec)

        def addcolor(encoding):
            new_e = encoding
            new_e.update({'color': self.color_encoding.vegalite})
            if self.mark == 'arc' and self.order_encoding:
                new_e.update({'order': self.order_encoding})
            return new_e

        def extract_chart(obj, index):
            if isinstance(obj, dict):
                # tear down dictionary
                for k, v in obj.items():
                    if k == 'encoding':
                        if 'text' in v.keys(): continue
                        obj[k] = addcolor(v)
                        index += 1

                    if isinstance(v, (dict, list)):
                        extract_chart(v, index)

            elif isinstance(obj, list):
                # tear down list
                for e in obj:
                    if isinstance(e, (dict, list)):
                        extract_chart(e, index)
        def np_encoder(obj):
            if isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, datetime.datetime):
                return obj.__str__()

        extract_chart(spec, index=0)
        if self.transform: spec.update({'transform': self.transform})
        return {"filename": self.name, 
                "spec": json.dumps(spec, default=np_encoder)}
# ==============================================================================