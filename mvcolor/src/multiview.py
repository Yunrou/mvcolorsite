import numpy as np
from copy import copy, deepcopy
from random import randint
from time import time
import json
from .util.color import Color
from .util.multiview import MVConceptSetHandler, Concept2Coloridx, \
                            ColorAssignment, ColormapGeneration
from .util.color_encoding import ColorEncoding
# ==============================================================================
class Multiview():
    # --------------------------------------------------------------------------
    def __init__(self, views: list, gamma=0.3, 
                 min_color=1, max_color=9):
        # Main
        self.views = views
        self.recolor_views = []
        # Concept Grouping
        self.concept2color = dict()
        self.MVconceptsets = []
        self.mvcs = []
        self.MVcolorencoding = []
        self.concept2coloridx = dict()
        self.mvcs_id = 0
        self.mvcg_id = 0
        # Color Assignment
        self.G = []
        self.color_Xid_upairs = []
        self.NS = []
        self.MVcolor_Xids = []
        # Parameters
        self.infeasible = True
        self.gamma = gamma
        self.min_n_color = min_color
        self.max_n_color = max_color
    # --------------------------------------------------------------------------
    def __len__(self):
        return len(self.views)
    # --------------------------------------------------------------------------
    def preprocessing(self):
        '''
        Extract multiview color encoding candidates
        '''
        start = time()
        # Generate MV concept entity sets
        print("\x1b[33m[Generate MV concept set]\x1b[0m")
        MVconceptsets = MVConceptSetHandler.generator(self.views)

        # Preparations
        for mvcs in MVconceptsets: 
            mvcs.SPP_preparation()
            mvcs.solve(max_n_colors=10)
    
        self.MVconceptsets = MVconceptsets

        # Color Assignment

        print("preprocessing 時間：", time()-start)
    # --------------------------------------------------------------------------
    def init_MVcolorencoding(self, collection):
        '''
        Find the color encoding of each view and form MVcolorencoding
        '''
        MVcolorencoding = [ColorEncoding() for x in range(self.__len__())]
        for i, v in enumerate(self.views):
            ce = v.find_color_encoding(collection[i])
            v.set_color_encoding(ce)
            MVcolorencoding[i] = copy(ce)
        return MVcolorencoding
    # --------------------------------------------------------------------------
    def set_MVcolorencoding(self, MVcolorencoding):
        '''
        After colormap generation, set color encoding for each view, and 
        MVcolorencoding
        '''
        for i, v in enumerate(self.views):
            v.set_color_encoding(MVcolorencoding[i])
        self.MVcolorencoding = MVcolorencoding
    # --------------------------------------------------------------------------
    def print_infeasible(self):
        '''
        Return original MV and print error message
        '''
        recolor_views = []
        for v in self.views:
            recolor_views.append({"filename": v.name, 
                                  "spec": json.dumps(v.spec)})
        self.recolor_views = recolor_views
        print("Cannot find a solution")
    # --------------------------------------------------------------------------
    def recolor(self, colorscheme, param, mvcs_id, mvcg_id, cmd, bgcolor):
        '''
        Parameters
        ----------
        colorscheme : list
                      list of hexcolors
        
        param : dict
                keys=(min_color, max_color, beta, gamma, disabled)

        Results
        -------
        recolored_views : list
                          list of json {'filename': ..., 'spec': ...}
        '''
        start0 = time()
        print("\x1b[33m[Recolor (Multiview)]\x1b[0m")

        # 0. Set parameters
        default     = True if cmd == "default" else False
        gamma       = 0.3 if default else param['gamma'] # get slider gamma
        min_n_color = param['min_n_color']
        max_n_color = min(param['max_n_color'], len(colorscheme))

        self.min_n_color = min_n_color
        self.max_n_color = max_n_color

        if cmd in ("default", "concept_grouping") or (not self.G):
            # 1. Select the best MVCE w/ grouped concepts
            print("\x1b[33m[Concept Grouping]\x1b[0m")
            mvcs = self.MVconceptsets[mvcs_id]
            grouping, _, _mvcg_id, isTheme = mvcs.get_solution(mvcg_id, default=False)
            if default:
                grouping, mvcs_id, mvcg_id = MVConceptSetHandler.selector(self.MVconceptsets)
                mvcs = self.MVconceptsets[mvcs_id]
                isTheme = False
            self.mvcs_id = mvcs_id
            self.mvcg_id = mvcg_id

            # Generate concept 2 color idx mapping
            concept2coloridx = Concept2Coloridx.generator(mvcs, grouping, isTheme)
            self.concept2coloridx = concept2coloridx
        
            # Find color encoding and initialize color encoding for each view
            MVcolorencoding = self.init_MVcolorencoding(mvcs.collection)
            self.MVcolorencoding = MVcolorencoding

            # Color Assignment preparation
            G, color_Xid_upairs, NS, MVcolor_Xids = ColorAssignment.preparation(
                                                                MVcolorencoding,
                                                                concept2coloridx)
            self.G = G
            self.color_Xid_upairs = color_Xid_upairs
            self.NS = NS
            self.MVcolor_Xids = MVcolor_Xids

        # 2. Assign colors
        print("\x1b[33m[Assigning Colors]\x1b[0m")
        start = time()
        MVcolorencoding = self.MVcolorencoding
        concept2coloridx = self.concept2coloridx
        concept2hexcolor = ColorAssignment.run(concept2coloridx,
                                               copy(colorscheme),
                                               self.G,
                                               self.color_Xid_upairs,
                                               self.NS, 
                                               self.MVcolor_Xids,
                                               bgcolor,
                                               weight=gamma,
                                               default=(cmd == "concept_grouping"))
        print("color assignment time:", time()-start)
        self.gamma = gamma
        self.concept2hexcolor = concept2hexcolor

        # 3. Colormap Generation
        MVcolorencoding = ColormapGeneration.run(MVcolorencoding,
                                                 concept2hexcolor)
        self.set_MVcolorencoding(MVcolorencoding)

        recolor_views = []
        for v in self.views:
            view = v.recolor()
            recolor_views.append(view)

        self.recolor_views = recolor_views
        print("Total time:", time()-start0)
        return
# ==============================================================================