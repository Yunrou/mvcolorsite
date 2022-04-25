from time import time
import numpy as np
from numpy.linalg import norm
from scipy.spatial.distance import pdist, squareform
from copy import copy, deepcopy
from itertools import combinations, product
from constraint import *
import gurobipy as gp
from gurobipy import GRB

from .color import Color #hex2lab, n_distinct
from .ga import ga

from .mv_concept_set import MVConceptSet
from .concept_set_instance import ConceptSetInstance
# ==============================================================================
class MVConceptSetHandler():
    '''
    Handling MV concept set generation and selection.
    '''
    # --------------------------------------------------------------------------
    @classmethod
    def generate_constraints(cls, vertices):
        '''
        Generate hard constraints for any pair of vertices contain identitical elements.

        Parameters
        ----------
        vertices: list
                each vertex contains the domain of concept sets

        Results
        -------
        hard_constraints : list
                           [(0, 2), (2, 3), (4, 7)]
        '''
        hard_constraints = []
        
        for i, vertex_i in enumerate(vertices):
            for j, vertex_j in enumerate(vertices[i+1:]):
                if len(vertex_i) == 1 or len(vertex_j) == 1: continue
                if set(map(tuple, vertex_i)) == set(map(tuple, vertex_j)):
                    hard_constraints.append((i, i+1+j)) # i+1+j: pos of vertex_j

        return hard_constraints
    # --------------------------------------------------------------------------
    @classmethod
    def constraint_solver(cls, vertices):
        '''
        Considering constraints for consistency and repetition, then
        generate suggested solutions across multiview

        Parameters
        ----------
        vertices : list
                   each vertex contains the domain of suggested_CE.concepts

        Results
        -------
        solutions : list
        '''
        # Add vertices
        problem = Problem()
        for i, vertex in enumerate(vertices):
            problem.addVariable(i, vertex)

        # Add Constraints
        hard_constraints = cls.generate_constraints(vertices)
        for hard_constraint in hard_constraints:
            problem.addConstraint(lambda x, x_: x == x_, hard_constraint)
        solutions = problem.getSolutions()

        return solutions
    # --------------------------------------------------------------------------
    @classmethod
    def generate_collections(cls, views: list):
        '''
        Select a concept set for each view as a collection
        '''
        # Generate domains for constraint solving problem
        # variable: index of each view, domain: corresponding view's concept sets
        domains = np.zeros((len(views),), dtype=object)
        domain  = []

        for i, view in enumerate(views):
            for concept_set in view.concept_sets:
                constant = (list(concept_set)[0] == view.title)
                if constant:
                    domain.append(['constant'])
                else:
                    domain.append(list(concept_set))
            domains[i] = copy(domain)
            domain.clear()

        # Constraint Satisfication Problem
        solutions = cls.constraint_solver(domains)

        # Transform solutions into collections
        collections = [[] for x in range(len(solutions))]

        for i, sol in enumerate(solutions):
            collection = [set() for x in range(len(views))]
            for view_id, domain in sol.items():
                if domain == ['constant']:
                    collection[view_id] = {views[view_id].title}
                else:
                    collection[view_id] = set(domain)
            collections[i] = deepcopy(collection)

        return collections
    # --------------------------------------------------------------------------
    @classmethod
    def generator(cls, views: list) -> list:
        '''
        Generate MV concept sets (MVCS)

        Parameters
        ----------
        views : list
                list of views

        Results
        -------
        MVCSs : list
                list of MVConceptSets
        '''
        # Select a concept set for each view to form a MVConceptSet
        collections = cls.generate_collections(views)
        
        MVCSs = []

        for collection in collections:
            concept_set_instances = []
            concept_collection = []
            for view_id, concept_set in enumerate(collection):
                view        = views[view_id]
                title       = view.title
                content     = view.content
                mark_type   = view.mark
                cardinality = len(concept_set)

                # find corresponding color_encoding of the concept_set
                color_encoding = view.color_encodings[
                                    view.concept_sets.index(concept_set)
                                 ]
                colormap_type = color_encoding.colormap_type
                concepts      = color_encoding.concepts

                instance = ConceptSetInstance(concept_set=concepts,
                                              view_id=view_id,
                                              title=title,
                                              content=content,
                                              mark_type=mark_type,
                                              colormap_type=colormap_type,
                                              cardinality=cardinality)
                concept_set_instances.append(instance)
                concept_collection.extend(concepts)

            # MV concept set can only have less than 30 distinct concepts
            if len(set(concept_collection)) > 30: continue

            mvcs = MVConceptSet(collection=deepcopy(collection),
                                instances=deepcopy(concept_set_instances))
            MVCSs.append((mvcs, len(concept_collection)))
        MVCSs.sort(key=lambda x: x[1])

        return [x[0] for x in MVCSs]
    # --------------------------------------------------------------------------
    @classmethod
    def selector(cls, MVCSs) -> tuple:
        '''
        Select one MVCS with optimum score

        Parameters
        ----------
        MVCSs : list
                list of MVConceptSets


        Results
        -------
        MVCS : MVConceptSet
               selected MVConceptSet

        grouping : list
                   2-hierarchical list, list of tuples (grouping result)
        '''
        candidates = []
        for mvcs_id, mvcs in enumerate(MVCSs):
            view_grouping, score, mvcg_id, _ = mvcs.get_solution(0, default=True)

            if score == -np.inf: continue

            concepts = mvcs.concept_data['concept']
            uniq_values, counts = np.unique(concepts, return_counts=True)
            n_repetitions = counts.sum() - counts.shape[0]
            repetition_rate =  1+ (n_repetitions / len(concepts))
            
            score *= repetition_rate
            print("score", score)
            candidates.append(tuple([mvcs_id, mvcg_id, view_grouping, 
                                     score, n_repetitions]))
        if not candidates:
            return MVConceptSet(collection=[], instances=[]), list()

        # Pick maximum
        candidates.sort(key=lambda x: -x[3]) # sort by score, pick maximum
        
        mvcs_id, mvcg_id, view_grouping, score, _ = candidates[0]
        
        return view_grouping, mvcs_id, mvcg_id
# ==============================================================================
class MVConceptSetGrouping():
    # --------------------------------------------------------------------------
    @classmethod
    def run(cls, mvcs, min_groups, max_groups, beta):
        '''
        Iterate through MVCE

        Parameters
        ----------
        mvcs : MVConceptSet
         
        Results
        ------
        solution : list
                   list of pairings [(0, 1), (2), (3, 4)]

        score : float
                optimal objective value
        '''
        # Concept table generation:
        # row: index, columns: features
        instances        = mvcs.instances
        pairings         = mvcs.pairings
        A                = mvcs.A
        VI               = mvcs.VI
        SI               = mvcs.SI
        n_colors         = mvcs.n_colors
        n_pairings       = len(pairings)

        if mvcs.max_cardinality > max_groups: # infeasible
            return dict(), np.inf
        # IP model formulation
        m = gp.Model()

        # Disable log in console
        m.Params.LogToConsole = 0

        # Binary variables
        x = m.addMVar(n_pairings, vtype=GRB.BINARY, name="pairings")
        
        # Objective function
        m.setObjective((1-beta)*(VI @ x) + beta*(SI @ x), GRB.MINIMIZE)

        # Constraint 1: A conceptset instance must be in one and only one group
        # e = np.ones(shape=(len(instances),),)
        m.addConstr(A @ x == 1)
            
        # Constraint 2: Specify the minimun & maximum number of groups
        m.addConstr((n_colors @ x) >= min_groups, name="lowerbound")
        m.addConstr((n_colors @ x) <= max_groups, name="upperbound")

        m.optimize() 

        # Infeasible
        if m.status == 3: 
            return list(), np.inf

        print("\x1b[34mGrouping result (Feasible):\x1b[0m")
        solution = []
        for i, v in enumerate(m.getVars()):
            if v.x == 1: 
                solution.append(pairings[i])
                print("===== pairing", i, "=====")
                for j in pairings[i]:
                    print(instances[j].concept_set, end=", ")
                print("")

        score = float('%g' % m.objVal)

        return solution, score
# ==============================================================================
class Concept2Coloridx:
    # --------------------------------------------------------------------------
    @classmethod
    def generator(cls, mvcs, grouping, isTheme):
        '''
        Convert grouping solution to mapping of concept2coloridx

        Parameters
        ----------
        mvcs : MVConceptSet
               
        grouping : list
                   2-hierarchical list, list of pairings (tuple)
                        
        Results
        -------
        concept2coloridx : dict
                           a mapping from concept to color index
        '''
        concept2coloridx = dict()
        concept_data = mvcs.concept_data

        color_id = 0
        
        for i, pairing in enumerate(grouping):
            subgrouping = mvcs.concept_grouping(pairing, isTheme)
            for j, subgroup in enumerate(subgrouping):
                addcolor = False
                for concept_instance_id in subgroup:
                    ce = concept_data[concept_instance_id]
                    if ce['constrained'] == True: continue
                    concept2coloridx.update({ ce['concept']: color_id})
                    addcolor = True

                color_id += 1 if addcolor == True else 0

        return concept2coloridx
        
# ==============================================================================
class ColorAssignment():
    # --------------------------------------------------------------------------
    @classmethod
    def preparation(cls, MVcolorencoding, concept2color_Xid):
        # MVcolor_Xids
        MVcolor_Xids = cls.get_MVcolor_Xids(MVcolorencoding, concept2color_Xid)
        
        # Within-View Color Difference Preparation
        # G1, color_Xid_upairs1 = cls.WVCD_preparation(MVcolor_Xids)
        # Between-View Color Difference Preparation
        G1, color_Xid_upairs1 = cls.BVCD_preparation(MVcolor_Xids)
        # Point Distinctness Preparation set G and color_Xid upairs
        G2, color_Xid_upairs2, NS, MVcolor_Xids = cls.PD_preparation(
                                                    MVcolorencoding, 
                                                    concept2color_Xid)
        # Point Contrast with Background Preparation 
        # G3, color_Xid = cls.PCwBG_preparation(MVcolorencoding, concept2color_Xid)

        G = [G1, G2]
        color_Xid_upairs = [color_Xid_upairs1, 
                            color_Xid_upairs2]

        return G, color_Xid_upairs, NS, MVcolor_Xids
    # --------------------------------------------------------------------------
    @classmethod
    def run(cls, concept2color_Xid, colorscheme, G, color_Xid_upairs,
            NS, MVcolor_Xids, bgcolor, weight, default=True):
        '''
        Assign colors to concepts.

        Parameters
        ----------
        MVcolorencoding : list
                          list of color encoding for each View

        concept2color_Xid : dict
                           mapping from concept to color idx

        colorscheme : list
                      colorscheme, list of hexcolors 
        
        weight : float
                 tuning weight

        default : bool
                  if True, assign colors in default order

        Results
        -------
        concept2hexcolor : dict
                           global colormap, a mapping from concept to hexcolor
        '''
        startTime = time()
        if default == False:
            reordered_colorscheme = []
            n_colors = len(colorscheme)

            # Precompute color pairwise distance
            color_pd = cls.calc_color_pd(colorscheme)

            # Precompute luminance distance with background color for all colors
            ldiffwBG = cls.calc_ldiffwBG(colorscheme, bgcolor)

            G1, G2 = G
            color_Xid_upairs1, color_Xid_upairs2 = color_Xid_upairs
            def fitness_function(X):
                '''
                X: [2, 3, 1, 0, 4, 5, ...] reorder indices of colorscheme
                '''
                X = np.array(X, dtype=np.uint8)
                h = cls.heuristic(X, color_pd, ldiffwBG, weight, G1, G2, 
                                  color_Xid_upairs1, 
                                  color_Xid_upairs2, NS, MVcolor_Xids)
                return h,
                
            # Rank
            sol = ga(fitness_function, 
                     _range=np.arange(n_colors), 
                     genome_length=n_colors,
                     pop_size=50, iterations=400, cxpb=0.6, mutpb=0.01)

            # Assign colors
            reordered_colorscheme = [colorscheme[i] for i in sol]
        else:
            reordered_colorscheme = colorscheme
        concept2hexcolor = copy(concept2color_Xid)
        for concept, color_Xid in concept2color_Xid.items():
            concept2hexcolor[concept] = reordered_colorscheme[color_Xid]
        
        return concept2hexcolor
    # --------------------------------------------------------------------------
    @classmethod
    def calc_color_pd(cls, colorscheme):
        labcolors = np.array([Color.hex2lab(c) for c in colorscheme])
            
        n_colors = len(colorscheme)
        color_pd = np.zeros((n_colors, n_colors))

        for i in range(n_colors):
            for j in range(i + 1, n_colors):
                color_pd[i,j] = Color.ciede2000(labcolors[i], labcolors[j])
                color_pd[j,i] = color_pd[i,j]

        return color_pd
    # --------------------------------------------------------------------------
    @classmethod
    def calc_ldiffwBG(cls, colorscheme, bgcolor):
        '''
        ldiffwBG : shape=(n_colors in colorscheme,)
        '''
        # luminances
        Ls = np.array([Color.hex2lab(c)[0] for c in colorscheme])
        n_colors = len(colorscheme)
        # Luminance of background color
        L_bg = Color.hex2lab(bgcolor)[0]
        # Luminance difference with background color
        ldiffwBG = np.abs(Ls - L_bg)
        # print("Ls, L_bg, ldiffwBG", Ls, L_bg, ldiffwBG)

        # labcolors = np.array([Color.hex2lab(c) for c in colorscheme])
        # n_colors = len(colorscheme)
        # lab_bg = Color.hex2lab(bgcolor)
        # ldiffwBG = np.zeros((n_colors,))
        # for i in range(n_colors):
        #     ldiffwBG[i] = Color.ciede2000(labcolors[i], lab_bg)

        return ldiffwBG
    # --------------------------------------------------------------------------
    @classmethod
    def get_MVcolor_Xids(cls, MVcolorencoding, concept2color_Xid):
        MVcolor_Xids = np.zeros((len(MVcolorencoding),), dtype=object)
        for i, ce in enumerate(MVcolorencoding):
            MVcolor_Xids[i] = np.array([concept2color_Xid[c] \
                                       for c in ce.concepts], dtype=np.uint8)

        return MVcolor_Xids
    # --------------------------------------------------------------------------
    @classmethod
    def WVCD_preparation(cls, MVcolor_Xids):
        '''
        Within-View Color Difference
        '''
        G, color_Xid_upairs = np.zeros((0,)), np.zeros((2,0), dtype=np.uint8)
        
        N = 0
        for color_Xids in MVcolor_Xids.tolist():
            if len(color_Xids) < 2: continue
            
            color_Xid_pairs = np.array(list(combinations(color_Xids, 2)), 
                                       dtype=np.uint8).T # (2, n_pairs)
            n_pairs = color_Xid_pairs.shape[1]
            g = np.ones((n_pairs,)) / n_pairs
            color_Xid_upairs = np.concatenate((color_Xid_upairs, 
                                               color_Xid_pairs), axis=1)
            G = np.concatenate((G, g), axis=0)
            N += 1

        G = G / N

        # Find distinct color_Xid pairs in concatenated color_Xid upairs
        u, inv = np.unique(color_Xid_upairs, return_inverse=True, axis=1)
        R = np.zeros(shape=(len(G),len(u.T)), dtype=int)
        R[np.arange(len(G)), inv] = 1

        G = G.T @ R
        color_Xid_upairs = u

        return G, color_Xid_upairs
    # --------------------------------------------------------------------------
    @classmethod
    def BVCD_preparation(cls, MVcolor_Xids):
        G, color_Xid_upairs = np.zeros((0,)), np.zeros((2,0), dtype=np.uint8)
        
        n_colormaps = len(MVcolor_Xids)

        for cm_pair in combinations(range(n_colormaps), 2):
            TwoVcolor_Xids = MVcolor_Xids[list(cm_pair)]
            color_Xid_pairs = np.array([list(pair) for pair in \
                                       product(*TwoVcolor_Xids)],
                                       dtype=np.uint8).T
            n_pairs = color_Xid_pairs.shape[1]
            g = np.ones((n_pairs,)) / n_pairs
            color_Xid_upairs = np.concatenate((color_Xid_upairs, 
                                               color_Xid_pairs), axis=1)
            G = np.concatenate((G, g), axis=0)

        n_pairs = (n_colormaps*(n_colormaps-1))/2
        G = G / n_pairs

        # Find distinct color_Xid pairs in concatenated color_Xid upairs
        u, inv = np.unique(color_Xid_upairs, return_inverse=True, axis=1)
        R = np.zeros(shape=(len(G),len(u.T)), dtype=int)
        R[np.arange(len(G)), inv] = 1

        G = G.T @ R
        color_Xid_upairs = u

        return G, color_Xid_upairs
    # --------------------------------------------------------------------------
    @classmethod
    def PD_preparation(cls, MVcolorencoding, concept2color_Xid):
        '''
        Point distinctness preparation
        '''
        G, color_Xid_upairs = np.zeros((0,)), np.zeros((2,0), dtype=np.uint8)

        # non-separability
        NS, MVcolor_Xids      = np.zeros((0,)), np.zeros((0,), dtype=np.uint8)
        
        # #(views) with more than one color
        N                   = 0
        for ce in MVcolorencoding:
            if ce.colormap_type != 'nominal' or ce.cardinality < 2: 
                ns = np.array([1], dtype=np.uint8) #* (1-_lambda)
                NS = np.concatenate((NS, ns), axis=0)
                color_Xids = np.array([concept2color_Xid[ce.concepts[0]]], 
                                       dtype=np.uint8)
                MVcolor_Xids = np.concatenate((MVcolor_Xids, color_Xids), axis=0)
                continue
            
            points    = ce.points
            n_points  = len(points)
            k = 5 if n_points > 5 else n_points - 1 # K nearest neighbors, K = 2

            positions = points[:,:2] # shape=(n_points, 2): x, y
            labels    = points[:,2]  # shape=(n_points,): concepts

            pos_pd       = squareform(pdist(positions))
            topK_indices = pos_pd.argsort(axis=1)[:,1:k+1] # (n_points,k)
            D            = pos_pd[np.arange(n_points),topK_indices.T].T # (n_points,k)
            D[D == 0]    = np.inf
            g            = np.divide(1,D)
            # g            = (g - g.min())/(g.max()-g.min()) # scaling
            
            
            # for point contrast with background: NS, color_Xids
            # Delta: record whether label_i and label_j are the same.
            # same: delta_ij = 1; diff: delta_ij = 0
            Delta = np.identity(n_points, dtype=np.uint8)
            for i in range(n_points):
                for j in range(i+1, n_points):
                    if labels[i] == labels[j]:
                        Delta[i, j] = 1
                        Delta[j, i] = 1
            Delta_bar = 1 - Delta
            A = Delta[np.arange(n_points),topK_indices.T].T * g.copy()
            B = Delta_bar[np.arange(n_points),topK_indices.T].T * g.copy()
            ns = np.dot(B-A, np.ones(shape=(k,1))).ravel() # shape=(n_points,)
            # ns = np.ones((n_points,), dtype=np.uint8)/(k*n_points)
            ns = ns / (k*k*n_points)
            NS = np.concatenate((NS, ns), axis=0)

            g            /= (k*n_points)#g.sum()
            g = g.ravel() # (k*n_points,)

            # shape=(n_points,)
            # map labels from concept to color Xid
            color_Xids = np.fromiter((concept2color_Xid[x] for x in labels), 
                                      dtype=np.uint8).reshape(labels.shape)
            MVcolor_Xids = np.concatenate((MVcolor_Xids, color_Xids), axis=0)

            # Concatenate into color_Xid pairs (2,k * n_point)
            color_Xid_pairs = np.array([np.repeat(color_Xids, k),
                                        color_Xids[topK_indices.ravel()]], 
                                        dtype=np.uint8)

            # Find distinct color_Xid pairs and map 
            u, inv = np.unique(color_Xid_pairs, return_inverse=True, axis=1)
            R = np.zeros(shape=(len(g),len(u.T)), dtype=int)
            R[np.arange(len(g)), inv] = 1

            G = np.concatenate((G, g.T @ R), axis=0) # (n_unique pairs,)
            color_Xid_upairs = np.concatenate((color_Xid_upairs, u), 
                                               axis=1) # (2, n_unique pairs)
            N += 1
        
        # Find distinct color_Xid pairs in concatenated color_Xid upairs
        u, inv = np.unique(color_Xid_upairs, return_inverse=True, axis=1)
        R = np.zeros(shape=(len(G),len(u.T)), dtype=int)
        R[np.arange(len(G)), inv] = 1
        # G = G / N
        G = (G.T @ R)
        color_Xid_upairs = u

        G /= N#len(MVcolorencoding)
        NS /= len(MVcolorencoding)

        return G, color_Xid_upairs, NS, MVcolor_Xids
    # --------------------------------------------------------------------------
    @classmethod
    def heuristic(cls, X, color_pd, ldiffwBG, weight, 
                  G1, G2, color_Xid_upairs1, color_Xid_upairs2, 
                  NS, MVcolor_Xids):
        '''
        Parameters
        ----------
        X : 1darray

        color_pd : ndarray
                   pairwise distance matrix of original colorscheme

        weight : float
                 weight to balance between intra- and 
                 inter-view color difference

        Results
        -------
        heuristic : float
        '''
        # WVCD = cls.calc_measure(X, color_pd, G1, color_Xid_upairs1)
        BVCD  = cls.calc_measure(X, color_pd, G1, color_Xid_upairs1)
        PD    = cls.calc_measure(X, color_pd, G2, color_Xid_upairs2)
        # Point Contrast with Background
        PCwBG = cls.calc_PCwBG(X, ldiffwBG, NS, MVcolor_Xids)
        # print("BVCD, PD, PCwBG", np.round(BVCD,2), np.round(PD,2), np.round(PCwBG,2))
        return (1-weight) * (0.5*PD+0.5*PCwBG) + weight * BVCD
    # --------------------------------------------------------------------------
    @classmethod
    def calc_measure(cls, X, color_pd, G, color_Xid_upairs):
        '''
        G : (n_pairs,)
        color_Xid_upairs : (2, n_pairs)
        '''
        color_id_upairs = np.fromiter((X[x] for x in color_Xid_upairs.ravel()),
                                      dtype=np.uint8).reshape(color_Xid_upairs.shape)

        i, j = color_id_upairs
        measure = G.T @ color_pd[i, j]
        return measure
    # --------------------------------------------------------------------------
    @classmethod
    def calc_PCwBG(cls, X, ldiffwBG, NS, MVcolor_Xids):
        '''
        ldiffwBG : (#colors in colorscheme,)
        NS : (#points in total of all views,)
        MVcolor_Xids : (#points in total of all views,)
        '''
        PCwBG = np.dot(NS.T, ldiffwBG[X[MVcolor_Xids]])
        return PCwBG
    # --------------------------------------------------------------------------
    @classmethod
    def pair_preference(cls, MVcolorencoding):
        pass
# ==============================================================================
class ColormapGeneration():
    # --------------------------------------------------------------------------
    @classmethod
    def run(cls, MVcolorencoding, concept2hexcolor):

        # Assign hexcolors
        # print(concept2hexcolor)
        for ce in MVcolorencoding:
            hexcolors = ['' for i in range(len(ce.concepts))]
            for i, concept in enumerate(ce.concepts):
                hexcolors[i] = concept2hexcolor[concept]
            ce.hexcolors = hexcolors

        # Set range
        for i, ce in enumerate(MVcolorencoding):
            ce.gen_colormap()
            ce.set_vegalite(ce.gen_vegalite())

        return MVcolorencoding
    # --------------------------------------------------------------------------
    def get_transform(cls, field, domain):
        '''
        for map, arc
        '''
        data = {"values": []}
        for i in range(len(domain)):
            data["values"].append({field: domain[i], "order": i+1})

        transform = [{
            "lookup": field,
            "from":{
                "data": data, 
                "key": field,
                "fields": ["order"]
            }
          }]

        return transform
# ==============================================================================