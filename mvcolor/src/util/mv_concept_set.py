import numpy as np
import numpy.linalg as LA
from copy import copy
import math
from itertools import product, combinations
import gurobipy as gp
from gurobipy import GRB

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.metrics import pairwise_distances, silhouette_score
from scipy.spatial.distance import cdist, cosine
from nltk import word_tokenize
from nltk.stem.snowball import SnowballStemmer

from time import time
# ==============================================================================
class MVConceptSet:
    # --------------------------------------------------------------------------
    def __init__(self, collection=[], instances=[]):
        self.collection        = collection
        self.instances         = instances

        # For view grouping
        self.data              = [] # concept-set data
        self.IW                = 0 # individual weight
        self.FVs               = [] # feature vectors

        self.pairings          = [] # pairings
        self.A                 = [] # matrix A for SPP
        self.CCs                = [] # visual consistency
        self.n_colors          = [] # #(color needs)
        self.vg_solutions      = [] # view grouping solutions
        self.default_sol       = [] # default solution

        # For concept grouping
        self.concept_data      = [] # concept data
        self.concept_pairings  = [] # concept instance pairings
        self.CD                = [] # concept distances
        self.OD                = [] # order distances
        self.conceptpairing_str2id = dict()
        self.n_concepts        = 0

        # High cardinality
        self.max_cardinality   = 0
    # --------------------------------------------------------------------------
    def __len__(self):
        return len(self.collection)
    # --------------------------------------------------------------------------
    def data_preparation(self, level='concept_set'):
        '''
        Parameters
        ----------
        level : str
                concept-set or concept level

        Results
        -------
        data : np.array
        '''
        if level == 'concept_set':
            instances = self.instances
            N = self.__len__()

            dt = [('concept_set', object), ('conceptid_set', object),
                  ('joined_concepts', 'U500'), 
                  ('title', 'U100'), ('content', 'U500'), ('mark_type', 'U100'), 
                  ('colormap_type', 'U100'), ('cardinality', np.uint8)]
            data = np.zeros((N,), dtype=dt)

            start = 0
            for i, e in enumerate(instances):
                # print(e.concept_set)
                joined_concepts = " ".join(e.concept_set)
                conceptid_set = list(range(start, start+e.cardinality, 1))
                data[i] = np.array((e.concept_set, conceptid_set, joined_concepts,
                                    e.title, e.content, e.mark_type, e.colormap_type,
                                    e.cardinality), dtype=dt)
                start += e.cardinality

            self.max_cardinality = max(data['cardinality'])
            return data

        elif level == 'concept':
            data = self.data
            N = sum(data['cardinality'])
            dt = [('concept_set_id', np.uint8), ('concept', 'U100'), 
                  ('order', np.uint8), ('constrained', bool)]
            concept_data = np.zeros((N,), dtype=dt)

            idx = 0
            for i, datum in enumerate(data):
                for order, concept in enumerate(datum['concept_set']):
                    constrained = concept in np.unique(concept_data['concept'])
                    concept_data[idx] = np.array((i, concept, order, constrained),
                                                   dtype=dt)
                    idx += 1

            return concept_data
    # --------------------------------------------------------------------------
    def calc_IW(self):
        '''
        calculate individual weight
        '''
        data  = self.data
        n_concepts = len(np.unique(self.concept_data['concept']))# - n_constant
        n_views = self.__len__()

        def individual_weight(x):
            if n_concepts <= 9:
                return 0.5
            else:
                return 0.1

        IW = np.asarray([individual_weight(x) \
                         for x in data['colormap_type']], dtype=np.float64)

        return IW
    # --------------------------------------------------------------------------
    def my_tokenizer(self, doc):
        tokens = word_tokenize(doc)
        snowball = SnowballStemmer('english')
        stems =  [snowball.stem(x) if x[-1] == 's' else x for x in tokens]
        return stems
   # --------------------------------------------------------------------------
    def calc_FVs(self):
        '''
        Calculate visual feature vectors
        '''
        N = self.__len__()
        def get_dummies(feature_values):
            # One-hot encoding: shape=(N,#(unique values))
            uniq_values = np.unique(feature_values)
            dummies = np.zeros((N,len(uniq_values)), dtype=int)
            mapped_values = [np.where(uniq_values == x)[0][0] \
                             for x in feature_values]
            dummies[np.arange(N), mapped_values] = 1
            return dummies

        data = self.data
        colormap_vectors = get_dummies(data['colormap_type'])
        mark_vectors = get_dummies(data['mark_type'])

        vectorizer = TfidfVectorizer(tokenizer=self.my_tokenizer,
                                     min_df=0.1, 
                                     max_df=0.9, 
                                     max_features=15)
        conceptset_vectors = np.asarray(vectorizer.fit_transform(
                                        data['joined_concepts']).todense())
        # vectorizer = TfidfVectorizer(tokenizer=self.my_tokenizer, max_df=1, max_features=8)
        title_vectors = np.asarray(vectorizer.fit_transform(data['title'])
                                   .todense())
        # vectorizer = TfidfVectorizer(tokenizer=self.my_tokenizer, max_df=0.8, max_features=8)
        content_vectors = np.asarray(vectorizer.fit_transform(data['content'])
                                     .todense())
        colormap_vectors = colormap_vectors / LA.norm(colormap_vectors, axis=1)[:,np.newaxis]
        mark_vectors = mark_vectors / LA.norm(mark_vectors, axis=1)[:,np.newaxis]
        conceptset_vectors = conceptset_vectors
        title_vectors = title_vectors
        content_vectors = content_vectors
        FVs = [colormap_vectors, mark_vectors, # visual feature vectors
               conceptset_vectors, title_vectors, content_vectors] # semantic feature vectors

        return FVs
        # Normalized to unit vectors
        # SF = SF / LA.norm(SF, axis=1)[:,np.newaxis]
    # --------------------------------------------------------------------------
    def SPP_preparation(self):
        # For concept-set grouping
        self.data  = self.data_preparation(level='concept_set')
        self.FVs   = self.calc_FVs()

        self.pairings = self.generate_pairings()
        self.A        = self.generate_A(len(self.instances), self.pairings)

        # For concept
        self.concept_data = self.data_preparation(level='concept')
        self.n_concepts   = len(np.unique(self.concept_data['concept']))
        start = time()
        self.conceptgrouping_preparation()
        print("conceptgrouping preparation:", time()-start)

        # For view grouping
        self.calc_measurements()
    # --------------------------------------------------------------------------
    def calc_measurements(self):
        pairings = self.pairings
        # self.VI = np.array([self.calc_VI(x) for x in pairings])
        # self.SI = np.array([self.calc_SI(x) for x in pairings])
        self.n_colors = np.array([self.calc_n_colors(x) for x in pairings])
    # --------------------------------------------------------------------------
    def calc_CV(self):
        '''
        Calculate concept semantic feature vectors
        '''
        data = self.concept_data
        vectorizer = TfidfVectorizer(tokenizer=self.my_tokenizer)
        concept_vectors = vectorizer.fit_transform(data['concept']).todense()
        
        CV = np.asarray(concept_vectors)

        return CV
    # --------------------------------------------------------------------------
    def calc_OV(self):
        '''
        Calculate order feature vectors
        '''
        data = self.concept_data
        order = data['order']
        order_feature = np.zeros((len(data),))
        if len(np.unique(order)) != 1:
            order_feature = (order-np.min(order))/(np.max(order)-np.min(order))

        OV = order_feature[:,np.newaxis]

        return OV
    # --------------------------------------------------------------------------
    def conceptgrouping_preparation(self):
        '''

        '''
        # Generate nested ids (local ids)
        data = self.data
        N = self.__len__()
        start      = 0
        nested_ids = [[] for x in range(N)]
        for i, datum in enumerate(data):
            cardinality = datum['cardinality']
            nested_ids[i] = list(range(start, start+cardinality, 1)) + [None]
            start += cardinality

        # Generate all concept-pairings, each pairing contains 
        # a tuple of concept instance ids
        concept_pairings = [tuple([x for x in p if x is not None]) \
                            for p in product(*nested_ids)]
        if tuple() in concept_pairings:
            concept_pairings.remove(())
        self.concept_pairings = concept_pairings

        cv = self.calc_CV()
        ov = self.calc_OV()
        concept_pd = pairwise_distances(cv, metric='cosine') 
        order_pd   = pairwise_distances(ov, metric='euclidean')

        self.CD = np.array([self.calc_CD(x, concept_pd) for x in concept_pairings])
        self.OD = np.array([self.calc_CD(x, order_pd) for x in concept_pairings])

        # Mapping
        self.conceptpairing_str2id = {"-".join(map(str, x)): i \
                                       for i, x in enumerate(concept_pairings)}
    # --------------------------------------------------------------------------
    def calc_CD(self, concept_pairing, pd):
        '''
        Precomputed concept semantic similarities of pairs of concept instances
        '''
        n = len(concept_pairing) # #(concept instances) in concept pairing
        if n == 1: return 0 # quick return

        indices = np.array([list(x) for x in combinations(concept_pairing, 2)]).T
        score = pd[indices[0], indices[1]].sum() / indices.shape[1]
        return score
    # --------------------------------------------------------------------------
    def concept_grouping(self, pairing, isTheme):
        '''
        Grouping concept instances in the pairing of concept-set instances
        '''
        subdata = self.data[list(pairing)]

        # Get nested_global_concept_ids and global_concept_ids
        constrained_gids = np.where(self.concept_data['constrained'] == True)[0]
        gids = np.array([y for y in sum([x for x in subdata['conceptid_set']], [])\
                         if y not in constrained_gids], 
                              dtype=np.uint8)
        # Quick return
        if len(pairing) == 1:
            return [[x] for x in gids]

        # Generate nested_local_concept_ids
        start            = 0
        nested_lids      = []
        nested_gids      = []
        max_cardinality  = max(subdata['cardinality'])

        for conceptid_set in subdata['conceptid_set']:
            sub_gids = [x for x in conceptid_set if x not in constrained_gids]
            cardinality = len(sub_gids)
            if cardinality == 0: continue
            max_cardinality = max(max_cardinality, cardinality)
            nested_gids.append(sub_gids+[None])
            nested_lids.append(list(range(start, start+cardinality, 1)) + [None])
            start += cardinality
            

        # Generate all sub pairings, each subpairing contains 
        # a tuple of local concept ids
        subpairings_l = [tuple([x for x in p if x is not None]) \
                       for p in product(*nested_lids)]
        subpairings_g = [tuple([x for x in p if x is not None]) \
                             for p in product(*nested_gids)]
        if tuple() in subpairings_l:
            subpairings_l.remove(())
        if tuple() in subpairings_g:
            subpairings_g.remove(())

        # Filter subpairings such that the same concepts should be 
        # in the same subpairing
        # print("Total Subpairings", len(subpairings_l))

        concept_pairings = self.concept_pairings # global concept pairings

        str2id = self.conceptpairing_str2id
        sub_concept_pairings_ids = [str2id["-".join(map(str, x))]\
                                     for x in subpairings_g]
        
        # Generate A
        A = self.generate_A(len(gids), subpairings_l)
        
        CD = self.CD[sub_concept_pairings_ids] # concept semantic similarities
        OD = self.OD[sub_concept_pairings_ids] # order distances
        
        
        # IP model formulation
        m = gp.Model()
        # Disable log in console
        m.Params.LogToConsole = 0

        # Binary variables
        x = m.addMVar(len(subpairings_l), vtype=GRB.BINARY, name="subpairings")
        
        # Objective function
        if not isTheme:
            m.setObjective(CD @ x + OD @ x, GRB.MINIMIZE)
        else:
            m.setObjective(OD @ x, GRB.MINIMIZE)

        # Constraint 1: A concept instance must be in one and only one group
        m.addConstr(A @ x == 1)

        # Constraint 2
        m.addConstr(x.sum() == int(max_cardinality), name="equality")
        
        m.optimize() 

        # Infeasible
        if m.status == 3: 
            # print("infeasible")
            return [[x] for x in gids]

        # Get grouping solution
        grouping = []
        for i, v in enumerate(m.getVars()):
            if v.X == 1:
                grouping.append([gids[y] for y in subpairings_l[i]])

        return grouping
    # --------------------------------------------------------------------------
    def calc_n_colors(self, pairing):
        '''
        only those have overlapped concepts should 
        '''
        # Check if the pairing need to do concept grouping to get #(colors)
        sub_conceptid_sets = [x for x in self.data[list(pairing)]['conceptid_set']]
        concept_gids = np.array(sum(sub_conceptid_sets, []), 
                                dtype=np.uint8)

        concept_data = self.concept_data

        if np.any(concept_data[concept_gids]['constrained']) == False:
            return max([len(x) for x in sub_conceptid_sets])
        else:
            # check if the concept of constrained concept instances
            constrained_gids = np.where(concept_data['constrained'] == True)[0]
            concepts = concept_data[constrained_gids]['concept']
            same_concept_gid_set = set(sum([np.where(concept_data['concept']\
                                            == x)[0].tolist() \
                                            for x in concepts], []))
            if len(same_concept_gid_set.intersection(set(concept_gids))) == \
               len(same_concept_gid_set):
               return max([len(x) for x in sub_conceptid_sets])

        # Concept grouping
        grouping = self.concept_grouping(pairing, isTheme=False)
        return len(grouping)
    # --------------------------------------------------------------------------
    def generate_A(self, n_instances, pairings):
        n_rows = n_instances # rows: concept-set instances/concept instances
        n_cols = len(pairings) # columns: pairings
        A = np.zeros(shape=(n_rows,n_cols), dtype=int)
        for i, p in enumerate(pairings):
            A[np.array(p), i] = 1
        return A
    # --------------------------------------------------------------------------
    def generate_pairings(self):
        '''
        Generate all legal pairings.

        Results
        -------
        pairings : list 
                   list of tuples, represents A in SPP.
        '''
        instances = self.instances # Concept-Set Instances
        N = self.__len__()
        
        instance_ids = range(N)
        pairings = []
        for i in range(N+1):
            pairings.extend(list(combinations(instance_ids, i)))
        pairings.remove(())

        # Reduce illegal pairings that are inconsistent
        pairings, _ = self.filter_pairings(pairings, instances, 
                                           level='concept_set')

        return pairings
    # --------------------------------------------------------------------------
    def find_constraints(self, instances, level='concept_set'):
        
        hard_constraints = []

        if level == 'concept_set':
            for i, instance_i in enumerate(instances):
                for j, instance_j in enumerate(instances[i+1:]):
                    # two concept-set instances have the same concept set.
                    if set(instance_i.concept_set) == set(instance_j.concept_set):
                        hard_constraints.append({i, i+1+j})

        elif level == 'concept':
            # Find indices of repeated values in an 1-d array as 
            # hard constraints
            vals, inverse, count = np.unique(instances, 
                                     return_inverse=True, 
                                     return_counts=True)

            repeated_vals_idx = np.where(count > 1)[0]
            repeated_vals = vals[repeated_vals_idx]

            rows, cols = np.where(inverse == repeated_vals_idx[:, np.newaxis])
            _, inverse_rows = np.unique(rows, return_index=True)
            hard_constraints = np.split(cols, inverse_rows[1:])
            hard_constraints = [set(hc) for hc in hard_constraints]

        return hard_constraints
    # --------------------------------------------------------------------------
    def filter_pairings(self, pairings, instances, level='concept_set'):
        '''
        Reduce illegal pairings that are inconsistent

        Paramenters
        -----------
        pairings : list
                   list of tuples, represents A that haven't filtered in SPP.

        Results
        -------
        remained_pairings : list
                            list of tuples, represent A that have filtered in SPP.
        '''
        
        # Find hard constraints s.t. the two concept-set instances have
        # the same concept sets will be grouped together
        hard_constraints = self.find_constraints(instances, level=level)
        constrained_ids = set([x for hc in hard_constraints for x in hc])
        
        # Filter
        filter_indices = np.empty(0, dtype=int)
        for i, pairing in enumerate(pairings):
            intersection = set(pairing).intersection(constrained_ids)
            if not intersection: continue

            for hc in hard_constraints:
                intersection = set(pairing).intersection(hc)
                if not intersection: continue
                elif intersection == hc: continue
                filter_indices = np.concatenate((filter_indices, np.ravel([i])))

        remained_indices = np.setdiff1d(np.arange(len(pairings)), filter_indices)
        remained_pairings = [pairings[x] for x in remained_indices]

        return remained_pairings, remained_indices

    # --------------------------------------------------------------------------
    def solve(self, max_n_colors):
        FVs = self.FVs
        self.IW = self.calc_IW() #0.000001 if self.n_concepts > 9 else 0.5
        VF = self.concatenate_vectors(FVs[:2], _type='visual')
        SF = self.concatenate_vectors(FVs[2:], _type='semantics')
        VSF = self.concatenate_vectors([VF, SF], _type='visual+semantics')

        pairings = self.pairings
        Vpd = pairwise_distances(VF, metric='cosine')
        Spd = pairwise_distances(SF, metric='cosine')
        VSpd = pairwise_distances(VSF, metric='cosine')
        n_views = self.__len__()
        VC = np.array([self.calc_consistency(x, VF, Vpd) for x in pairings])
        SC = np.array([self.calc_consistency(x, SF, Spd) for x in pairings])
        VSC = np.array([self.calc_consistency(x, VSF, VSpd) \
                        for i, x in enumerate(pairings) ])
                   # if ((VC[i] != -n_views) or (SC[i] != -n_views)) else -n_views\
        self.CCs = [VSC, VC, SC]
        self.pds = [VSpd, Vpd, Spd]
        #np.max([self.VC, self.SC], axis=0)# 0.5*self.VC+0.5*self.SC#
        self.vg_solutions = self.generate_view_groupings(max_n_colors)
    # --------------------------------------------------------------------------
    def get_solution(self, _index, default):
        vg_solutions = self.vg_solutions
        sol = vg_solutions[_index]
        if default:
            if not self.default_sol:
                return [], -np.inf, -1, False
            sol = self.default_sol
        isTheme = True if sol['consistency'] == '0_theme' else False
        # print("insighttype", sol['insight_type'])
        return sol['view_grouping'], sol['score'], sol['index'], isTheme
    # --------------------------------------------------------------------------
    def calc_consistency(self, pairing, feature_vectors, pd):
        '''
        Calculate Visual Inconsistency of the pairing j
        '''
        Nj       = len(pairing)
        vectors = feature_vectors[list(pairing)]# shape=(Nj,n_features)
        n_views = len(feature_vectors)
        
        # min_similarity = 1
        # for index_ in combinations(pairing, 2):
        #     min_similarity = min(min_similarity, 1-pd[index_])
        #     if pd[index_] == 1: 
        #         return 0
        non_pairing = [x for x in range(n_views) if x not in pairing]
        if non_pairing:
            for index_ in product(*[list(pairing),non_pairing]):
                if pd[index_] == 0: 
                    return -n_views

        centroid = np.mean(vectors, axis=0) # shape=(1,n_features)
        centroid = centroid / LA.norm(centroid) # scaling to unit vector

        # cosine similarity from centroid to each vector, shape=(Nj,)
        # Within similarity
        WS = 1 - cdist(vectors, centroid[np.newaxis,:], metric='cosine').ravel()
        # Calculate average within cluster similarity
        # using cosine similarity as consistency
        iw = self.IW[pairing[0]]
        # print(iw.shape, WS.shape)
        WS = WS.sum() / Nj

        n_fvs = len(feature_vectors)

        # Calculate cosine similarity between centroids of 2 partitions: pairing j and j'
        # Centroid similarity
        centroid_similarity = 0
        # Constraint:
        if Nj < n_views:
            other_vectors = feature_vectors[[x for x in range(n_views) \
                                             if x not in pairing]]
            centroid_ = np.mean(other_vectors, axis=0)
            centroid_ = centroid_ / LA.norm(centroid_)
            centroid_similarity = 1 - cosine(centroid_, centroid)

        CC = WS/(centroid_similarity+1)

        if Nj > 1:
            CC *= 1
        else:
            CC *= iw

        return CC
    # --------------------------------------------------------------------------
    def generate_view_groupings(self, max_n_colors):
        '''
        Genearete all possible optimal view groupings for each #(colors) and #(views)
        '''
        min_n_colors = self.max_cardinality
        n_instances = len(self.instances)
        pairings = self.pairings
        dt = [('consistency', 'U100'), ('n_colors', int), ('n_pairings', int), 
              ('view_grouping', object), ('score', float), ('index', int)]

        vg_solutions = np.zeros((0,), dtype=dt)
        # theme color
        sol = np.array([('0_theme', min_n_colors, 1, [tuple(range(n_instances))], 
                         0, 0)], dt)
        vg_solutions = np.concatenate((vg_solutions, sol), axis=0)

        consistency_options = ['1_visual+semantics', '2_visual', '3_semantics']
        CCs = self.CCs

        set_default = False
        _index = 1
        for i, option in enumerate(consistency_options):
            num = int(option.split('_')[0])
            weight = 0.5 if num == 1 else 1 if num == 2 else 0
            upper_bound = max_n_colors
            while upper_bound > min_n_colors:
                vg, score, n_colors = self.view_grouping(weight,
                                                         CC=CCs[i],
                                                         min_n_colors=min_n_colors, 
                                                         max_n_colors=upper_bound)
                if score == np.inf: 
                    upper_bound -= 1
                    continue
                # labels = np.zeros(shape=(n_instances,), dtype=int)
                # for j, group in enumerate(vg):
                #     for k in group: labels[k] = int(j)
                # ss = silhouette_score(self.pds[i], labels, metric="precomputed")
                sol = np.array([(option, n_colors, len(vg), vg, score, _index)], dt)
                if (not set_default) and (option == '1_visual+semantics') and \
                    (n_colors <= 9):
                    self.default_sol = sol[0]
                    set_default = True
                
                vg_solutions = np.concatenate((vg_solutions, sol), axis=0)
                _index += 1
                upper_bound = n_colors - 1

        # vg_solutions.sort(order=['consistency', 'ss'])#'n_colors', 'n_pairings'])
        return vg_solutions
    # --------------------------------------------------------------------------
    def concatenate_vectors(self, FVs, _type='visual'):

        w = np.zeros((0,))
        if _type == 'visual':
            w = np.concatenate([np.repeat(0.75, FVs[0].shape[1]),
                                np.repeat(0.25, FVs[1].shape[1])], axis=0)
        elif _type == 'semantics':
            w = np.concatenate([np.repeat(0.3, FVs[0].shape[1]),
                                np.repeat(0.3, FVs[1].shape[1]),
                                np.repeat(0.4, FVs[2].shape[1])], axis=0)
        elif _type == 'visual+semantics':
            w = np.concatenate([np.repeat(0.5, FVs[0].shape[1]),
                                np.repeat(0.5, FVs[1].shape[1])], axis=0)
        vectors = w * np.concatenate(FVs, axis=1)
        # Normalized to unit vectors
        vectors = vectors / LA.norm(vectors, axis=1)[:,np.newaxis]
        return vectors
    # --------------------------------------------------------------------------
    def view_grouping(self, weight, CC, min_n_colors, max_n_colors):
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
        instances        = self.instances
        n_views          = len(instances)
        pairings         = self.pairings
        A                = self.A
        n_colors         = self.n_colors
        n_pairings       = len(pairings)

        if self.max_cardinality > max_n_colors: # infeasible
            return dict(), np.inf
        # IP model formulation
        m = gp.Model()

        # Disable log in console
        m.Params.LogToConsole = 0

        # Binary variables
        x = m.addMVar(n_pairings, vtype=GRB.BINARY, name="pairings")
        
        # Objective function
        m.setObjective(CC @ x, GRB.MAXIMIZE)
        # m.setObjective(weight * (VC @ x) + (1-weight) * (SC @ x), GRB.MAXIMIZE)

        # Constraint 1: A conceptset instance must be in one and only one group
        # e = np.ones(shape=(len(instances),),)
        m.addConstr(A @ x == 1)
            
        # Constraint 2: Specify the minimun & maximum number of groups
        m.addConstr((n_colors @ x) >= min_n_colors, name="lowerbound")
        m.addConstr((n_colors @ x) <= max_n_colors, name="upperbound")
        m.addConstr((CC @ x) >= 0, name="feasible")
        # m.addConstr((weight * (VC @ x) + (1-weight) * (SC @ x)) >= 0, name="feasible")
        m.optimize() 

        # Infeasible
        if m.status == 3: 
            return list(), np.inf, -1
        # print("\x1b[34mGrouping result (Feasible):\x1b[0m", weight, max_n_colors)
                
        solution = []
        color_needs = 0
        VSC, VC, SC = self.CCs
        for i, v in enumerate(m.getVars()):
            if v.x == 1: 
                solution.append(pairings[i])
                color_needs += n_colors[i]
        #         print("===== pairing", i, "=====")
        #         for j in pairings[i]:
        #             print(instances[j].concept_set, end=", ")
        #         print(VC[i], SC[i], VSC[i])
        # print("colorneeds:", color_needs)
        score = float('%g' % m.objVal)
        return sorted(solution), score, color_needs
# ==============================================================================