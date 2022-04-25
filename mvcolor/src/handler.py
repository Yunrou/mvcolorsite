from copy import copy, deepcopy
import os, json
from .view import View
from .multiview import Multiview
from pandas import read_csv, read_json, DataFrame
from werkzeug.utils import secure_filename

class Handler():
    # config for only remaining marks
    config = {
            "view": {"stroke": None},
            "axis": {
              "grid": False,
              "ticks": False,
              "domain": False,
              "labelPadding": 5,
              "labels": False,
              "title": None
            },
            "legend": {
              "disable": True
            },
            "header": {
                "title": None,
                "labels": False
            }
        }
    # --------------------------------------------------------------------------
    @classmethod
    def recolor_spec(cls, spec: dict, ce_vegalite:dict, range_colors: list):

        # check validity
        if 'value' in ce_vegalite: # constant
            hexcolor = range_colors[0]
            ce_vegalite.clear() 
            ce_vegalite.update({"value": hexcolor})
            if 'color' in spec['encoding']:
                spec['encoding']['color'].clear()
        else:
            ce_vegalite['scale'].update({"range": range_colors})

        if 'color' in spec['encoding']:
            spec['encoding']['color'].update(ce_vegalite)
        else:
            spec['encoding'].update({"color": ce_vegalite})

        return json.dumps(spec)
    # --------------------------------------------------------------------------
    @classmethod
    def datasets2dfs(cls, dataset_objs):
        '''
        Transform data csv to dataframe
        '''
        dfs = {}
        for obj in dataset_objs:
            ext = obj.name.split('.')[-1]
            if ext == 'csv':
                dfs.update({obj.name: read_csv(obj.file)})
            elif ext == 'json':
                try:
                    dfs.update({obj.name: read_json(obj.file)})
                except:
                    pass
                    # dfs.update({obj.name: DataFrame(json.loads(obj.file.read()).items())})
        return dfs
    # --------------------------------------------------------------------------
    @classmethod
    def set_url(cls, spec: dict):

        dataset_url = os.path.join("../../media", "dataset")
        
        def extract(obj):
            if isinstance(obj, dict):
                for k, v in obj.items():
                    if k == 'url':
                        try:
                            dataset_name = secure_filename(v).split('/')[-1]
                            obj[k] = os.path.join(dataset_url, dataset_name)
                        except:
                            print("The dataset is not exist.")
                    if isinstance(v, (dict, list)):
                        extract(v)
            elif isinstance(obj, list):
                for e in obj:
                    if isinstance(e, (dict, list)):
                        extract(e)

        extract(spec)
        return spec
    # --------------------------------------------------------------------------
    @classmethod
    def createMV(cls, dataset_objs, chart_objs):
        '''
        Create MV instance and preprocessing it before user click recolor

        Parameters
        ----------
        dataset_objs : models.Model

        chart_objs : models.Model

        param : an object of type models.Parameter

        Results
        -------
        mv : Multiview
             A multiview instance
        '''
        dfs = cls.datasets2dfs(dataset_objs)
        views = [[] for x in range(len(chart_objs))]

        for obj in chart_objs:
            spec = json.loads(obj.raw_spec)
            print(obj.title)
            if not obj.dataset and "values" in spec["data"]:
                df = DataFrame(spec["data"]["values"])
                views[obj.index] = View(obj.name, obj.title, spec, df, cls.config)
            else:
                views[obj.index] = View(obj.name, obj.title, spec, dfs[obj.dataset], cls.config)

        mv = Multiview(views=views)
        mv.preprocessing()

        return mv
    # --------------------------------------------------------------------------
    @classmethod
    def recolor(cls, mv, color_objs, color_config, param, mvce_id, mvcg_id, cmd,
                isTheme):
        '''
        Parameters
        ----------
        mv : Multiview
             A multiview instance

        color_objs : models.Model

        color_config : ColorConfig.object

        param : dict

        Results
        -------
        recolor_views : list
                        list of recolored views' specs
        '''
        colorscheme = []
        for obj in color_objs:
            colorscheme.append(obj.color)

        print("Color Config:", color_config, color_config.bgcolor)
        bgcolor = color_config.bgcolor
        # Recolor
        mv.recolor(colorscheme, param, mvce_id, mvcg_id, cmd, bgcolor)

        return mv