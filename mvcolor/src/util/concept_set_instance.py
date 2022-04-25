class ConceptSetInstance():
    # --------------------------------------------------------------------------
    def __init__(self, concept_set=[], view_id=0, title='', content='', mark_type='', 
                 colormap_type='', cardinality=1):
        self.concept_set = concept_set
        self.view_id = view_id
        self.title = title
        self.content = content
        self.mark_type = mark_type
        self.colormap_type = colormap_type
        self.cardinality = cardinality