# Django
from django.conf import settings
from .models import Dataset, Chart, Color, ColorScheme, ColorConfig,\
                    Parameter, Example, ColorEncoding, RangeColor, \
                    MVColorEncoding, MVConceptGrouping
from django.core.files import File
from django.core.exceptions import ObjectDoesNotExist

# Rest_Framework
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
import io
from rest_framework.parsers import JSONParser

from rest_framework.views import APIView
from .serializers import ChartSerializer, ColorSerializer, DatasetSerializer,\
                         ColorSchemeSerializer, ColorConfigSerializer,\
                         ParameterSerializer, ExampleSerializer, \
                         ColorEncodingSerializer, RangeColorSerializer, \
                         MVColorEncodingSerializer, MVConceptGroupingSerializer
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
user_token = {'Authorization: Token 778b017b5f7a65ec655b4bf4d31e427eeadb2f4a'}

# Others
import os, json
from copy import copy, deepcopy
import numpy as np
from werkzeug.utils import secure_filename
from .src.handler import Handler
from .src.multiview import Multiview
from pandas import read_csv
import pickle5 as pickle
# ==============================================================================
class ChartViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.AllowAny]
    serializer_class = ChartSerializer
    
    mv = Multiview([])
    # --------------------------------------------------------------------------
    def create(self, request, *args, **kwargs):
        if request.method == 'POST':
            action = request.data["action"]

            if action == "recolor":
                param = request.data["param"]
                cmd = request.data["cmd"]
                example = Example.objects.get(current=True).value
                global mv
                if not len(mv): 
                    # return no chart
                    serializer = ChartSerializer(Chart.objects.filter(
                                                        example=example), 
                                                        many=True)
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                obj = MVConceptGrouping.objects.get(pk=param['mvcg_pk'])
                isTheme = (obj.consistency == "theme")
                mv = Handler.recolor(mv,
                                     Color.objects.filter(colorscheme='user'),
                                     ColorConfig.objects.get(name='user'),
                                     param, obj.mvce_id, obj.mvcg_id,
                                     cmd, isTheme)
                if mv.recolor_views:
                    try:
                        # recolor
                        MVcolorencoding = mv.MVcolorencoding
                        for i, chart in enumerate(mv.recolor_views):
                            # Set Charts
                            obj = Chart.objects.get(example=example,
                                                    name=chart['filename'])
                            if obj.spec != chart['spec']:
                                obj.spec = chart['spec']
                            ce = MVcolorencoding[i]

                            # print(ce._range)
                            ce_id = ColorEncoding.objects.get(
                                            chart_id=i, 
                                            field=ce.field
                                        ).ce_id
                            obj.ce_id = ce_id
                            obj.ce_field = ce.field
                            obj.save()

                            # Set RangeColors
                            for j, rc in enumerate(ce.hexcolors):
                                obj = RangeColor.objects.get(chart_id=i,
                                                             ce_id=ce_id,
                                                             range_id=j)
                                obj.hexcolor = rc
                                obj.save()
                        # Set Parameters
                        param = Parameter.objects.get(name='user')
                        mvcg = MVConceptGrouping.objects.get(mvce_id=mv.mvcs_id,
                                                             mvcg_id=mv.mvcg_id)
                        param.mvce_id = mv.mvcs_id
                        param.mvcg_pk = mvcg.pk
                        param.gamma = mv.gamma
                        param.isTheme = (mvcg.consistency == "theme")
                        if cmd == "default":
                            param.consistency = 'visual+semantics'
                        else:
                            param.consistency = mvcg.consistency

                        param.save()

                    except:
                        print(chart['filename'],chart['spec'])
                        print("oops!")

            elif action == "load_example":
                example = request.data["example"]
                mvcolor = request.data["MVcolor"] # whether MVcolor is enabled
                print(mvcolor)
                example_root = os.path.join(settings.MEDIA_ROOT, 'example', example)
                model_path = os.path.join(example_root, "model.sav")

                # Set the example's current to True
                obj = Example.objects.filter(current=True).first()
                if obj != None:
                    obj.current = False
                    obj.save()

                obj = Example.objects.filter(value=example).first()
                if obj != None:
                    obj.current = True
                    obj.save()
                
                objs = Chart.objects.filter(current=True)
                if objs.first() != None:
                    for obj in objs: 
                        obj.current=False
                        obj.save()
                # Clear ColorEncoding and RangeColor objects
                ColorEncoding.objects.all().delete()
                RangeColor.objects.all().delete()
                MVColorEncoding.objects.all().delete()
                MVConceptGrouping.objects.all().delete()

                # Get and Set Color Encoding (For human baseline)
                colorscheme = [x.color for i in range(2) for x in \
                               Color.objects.filter(colorscheme='user')]

                mv = pickle.load(open(model_path, 'rb'))
                for i, view in enumerate(mv.views):
                    color_encodings = view.color_encodings
                    ce_vegalite = ""
                    for j, ce in enumerate(color_encodings):
                        field = ce.field
                        concepts = ce.concepts
                        ce.hexcolors = colorscheme[:len(ce.concepts)]
                        print("concepts", ce.hexcolors, ce.concepts)
                        ce.gen_colormap()
                        _range = ce._range
                        ce_vegalite = json.dumps(ce.gen_vegalite())
                        name = field
                        if ce.constant: 
                            concepts = [""]
                            name = "single color"

                        for k, hexcolor in enumerate(ce.hexcolors):
                            obj = RangeColor.objects.create(chart_id=i, 
                                                            ce_id=j,
                                                            range_id=k,
                                                            concept=concepts[k],
                                                            hexcolor=hexcolor, 
                                                            mvcolor=mvcolor)
                        _range = json.dumps(_range)

                        obj = ColorEncoding.objects.create(chart_id=i,
                                                           ce_id=j,
                                                           field=field,
                                                           name=name,
                                                           vegalite=ce_vegalite)
                    # Update Coloring for each chart/view
                    range_colors = [x.hexcolor for x in RangeColor.objects.
                                                filter(chart_id=i,
                                                       ce_id=0)]
                    ce = ColorEncoding.objects.get(chart_id=i, ce_id=0)

                    ce_0 = view.color_encodings[0]
                    ce_0.hexcolors = range_colors
                    ce_0.gen_colormap()
                    ce_0.set_vegalite(ce_0.gen_vegalite())
                    view.set_color_encoding(ce_0)
                    spec = view.recolor()['spec']
                    if view.title == "City Breakdown": print(spec)

                    chart = Chart.objects.get(example=example, index=i)
                    chart.spec = spec
                    chart.ce_id = 0 # reset
                    chart.ce_field = ce.field
                    chart.current = True
                    chart.save()
                # Set the list of MV color encodings
                mvcg_pk = 0
                for i, mvce in enumerate(mv.MVconceptsets):
                    obj = MVColorEncoding.objects.create(mvce_id=i,
                                                         name="#"+str(i+1), 
                                                         value=str(i+1))
                    for j, sol in enumerate(mvce.vg_solutions):
                        consistency = sol['consistency'].split('_')[1]
                        if consistency == 'theme': 
                            name = 'default coloring'
                        else:
                            name = str(sol['n_colors']) + ' colors'
                        obj = MVConceptGrouping.objects.create(mvce_id=i,
                                                               mvcg_id=j,
                                                               name=name,
                                                               value=str(j+1),
                                                               consistency=consistency)
                        if i == 0 and j == 0:
                            # theme color
                            pk = obj.pk
                        
                # reset parameters
                param = Parameter.objects.filter(name='user').get()
                param.min_n_color = mv.min_n_color
                param.max_n_color = mv.max_n_color
                param.gamma = mv.gamma
                param.consistency = 'visual+semantics'
                param.mvce_id = 0
                param.mvcg_pk = pk
                param.isTheme = True
                param.save()

            serializer = ChartSerializer(Chart.objects.filter(example=example), many=True)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
    # --------------------------------------------------------------------------
    def get_queryset(self): #this method is called inside of get
        queryset = Chart.objects.filter(current=True)
        return queryset
    # --------------------------------------------------------------------------
    def update(self, request, *args, **kwargs):
        action = request.data["action"]
        ce_id = int(request.data["ce_id"])
        chart = self.get_object()
        ce = ColorEncoding.objects.get(chart_id=chart.index, ce_id=ce_id)
        range_colors = [x.hexcolor for x in RangeColor.objects.all()
                                            .filter(chart_id=chart.index,
                                                    ce_id=ce.ce_id)]
        chartview = mv.views[chart.index]
        chartce = chartview.color_encodings[ce_id]
        chartce.hexcolors = range_colors
        chartce.gen_colormap()
        chartce.set_vegalite(chartce.gen_vegalite())
        chartview.set_color_encoding(chartce)
        spec = chartview.recolor()['spec']
        # spec = json.loads(chart.spec)
        # ce_vegalite = json.loads(ce.vegalite)
        
        if action == 'set-ce':
            chart.ce_id = ce.ce_id
            chart.ce_field = ce.field

        # Update Coloring for each chart/view
        # spec = Handler.recolor_spec(spec, ce_vegalite, range_colors)
        chart.spec = spec
        chart.save()
        serializer = ChartSerializer(Chart.objects.filter(current=True), many=True)
        return Response(serializer.data)
    # --------------------------------------------------------------------------
    def destroy(self, request, *args, **kwargs):
        return super(ChartViewSet, self).destroy(request, *args, **kwargs)
# ==============================================================================
class ColorViewSet(viewsets.ModelViewSet):
    # authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [permissions.AllowAny]
    serializer_class = ColorSerializer
    # --------------------------------------------------------------------------
    def create(self, request, *args, **kwargs):
        if request.method == 'POST':
            action = request.data['action']
            # add color
            if action == 'addcolor':
                color = request.data['color']
                obj = Color.objects.create(color=color, 
                                           colorscheme='user')
                
            elif action == 'setcolors':
                colorscheme = request.data['colorscheme']
                Color.objects.filter(colorscheme='user').delete()

                for i in Color.objects.filter(colorscheme=colorscheme):
                    obj = Color.objects.create(color=i.color, colorscheme='user')

            elif action == 'swapcolors':
                pks = request.data['swapPks']
                colors = [Color.objects.get(pk=pk).color for pk in pks]

                for i, pk in enumerate(pks):
                    obj = Color.objects.get(pk=pk)
                    obj.color = colors[i-1]
                    obj.save()
                
            serializer = ColorSerializer(Color.objects.filter(colorscheme='user'), 
                                         many=True)
            return Response(serializer.data)
    # --------------------------------------------------------------------------
    def get_queryset(self): #this method is called inside of get
        queryset = Color.objects.filter(colorscheme='user')
        return queryset
    # --------------------------------------------------------------------------
    def destroy(self, request, *args, **kwargs):
        return super(ColorViewSet, self).destroy(request, *args, **kwargs)
# ==============================================================================
class ColorSchemeViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.AllowAny]
    serializer_class = ColorSchemeSerializer
    # --------------------------------------------------------------------------
    def create(self, request, *args, **kwargs):
        if request.method == 'POST':
            # Customized ColorScheme name
            customized_name = request.data['customized_name']
            for i in Color.objects.all().filter(colorscheme='user'):
                obj = Color.objects.create(color=i.color, colorscheme=customized_name)
            ColorScheme.objects.create(name=customized_name)

            serializer = ColorSchemeSerializer(ColorScheme.objects.all(), many=True)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
    # --------------------------------------------------------------------------
    def get_queryset(self): #this method is called inside of get
        queryset = ColorScheme.objects.all()
        return queryset
# ==============================================================================
class ColorConfigViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.AllowAny]
    serializer_class = ColorConfigSerializer
    # --------------------------------------------------------------------------
    def create(self, request, *args, **kwargs):
        if request.method == 'POST':
            # set background color, and text color
            data = request.data
            obj = ColorConfig.objects.get(name='user')

            if 'bgcolor' in data.keys():
                obj.bgcolor = data['bgcolor']
            elif 'textcolor' in data.keys():
                obj.textcolor = data['textcolor']
            obj.save()

            serializer = ColorConfigSerializer(ColorConfig.objects.filter(name='user'), 
                                               many=True)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
    # --------------------------------------------------------------------------
    def get_queryset(self): #this method is called inside of get
        queryset = ColorConfig.objects.all().filter(name='user')
        return queryset
# ==============================================================================
class DatasetViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.AllowAny]
    serializer_class = DatasetSerializer
    # --------------------------------------------------------------------------
    def create(self, request, *args, **kwargs):
        if request.FILES:
            for f in request.FILES.getlist('file'):
                f.name = secure_filename(f.name)
                
                if len(Dataset.objects.filter(name=f.name)):
                    Dataset.objects.get(name=f.name).delete()

                file = os.path.join(settings.MEDIA_ROOT, 'dataset', f.name)
                if os.path.isfile(file):
                    os.remove(file)
                # create instance
                obj = Dataset.objects.create(name=f.name, file=f)
            serializer = DatasetSerializer(Dataset.objects.all(), many=True)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
    # --------------------------------------------------------------------------
    def get_queryset(self): #this method is called inside of get
        queryset = Dataset.objects.all()
        return queryset
# ==============================================================================
class ExampleViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.AllowAny] 
    serializer_class = ExampleSerializer
    # --------------------------------------------------------------------------
    def get_queryset(self): #this method is called inside of get
        queryset = Example.objects.all()
        return queryset
# ==============================================================================
class ParameterViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.AllowAny] 
    serializer_class = ParameterSerializer
    # --------------------------------------------------------------------------
    def create(self, request, *args, **kwargs):
        if request.method == 'POST':
            param = request.data['param']
            # set object
            obj = Parameter.objects.all().filter(name='user').get()
            obj.min_n_color = param['min_n_color']
            obj.max_n_color = param['max_n_color']
            obj.gamma = param['gamma']
            obj.consistency = param['consistency']
            obj.mvce_id = param['mvce_id']
            obj.mvcg_pk = param['mvcg_pk']
            obj.isTheme = param['isTheme']
            obj.save()
            serializer = ParameterSerializer(Parameter.objects.all(), many=True)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
    # --------------------------------------------------------------------------
    def get_queryset(self): #this method is called inside of get
        queryset = Parameter.objects.all()
        return queryset
# ==============================================================================
class ColorEncodingViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.AllowAny]
    serializer_class = ColorEncodingSerializer
    # --------------------------------------------------------------------------
    def get_queryset(self): #this method is called inside of get
        queryset = ColorEncoding.objects.all()
        return queryset
# ==============================================================================
class RangeColorViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.AllowAny]
    serializer_class = RangeColorSerializer
    # --------------------------------------------------------------------------
    def create(self, request, *args, **kwargs):
        if request.method == 'POST':
            action = request.data['action']
            if action == 'swap':
                swapPks = request.data['swapPks']
                colors = [Color.objects.get(pk=pk).color for pk in swapPks]
                print(colors)
                rc_list = RangeColor.objects.filter(hexcolor=colors[0])
                for rc in rc_list:
                    rc.hexcolor = '#ffffff'
                    rc.save()
                rc_list = RangeColor.objects.filter(hexcolor=colors[1])
                for rc in rc_list:
                    rc.hexcolor = colors[0]
                    rc.save()
                rc_list = RangeColor.objects.filter(hexcolor='#ffffff')
                for rc in rc_list:
                    rc.hexcolor = colors[1]
                    rc.save()
                    
        serializer = RangeColorSerializer(RangeColor.objects.all(), many=True)
        return Response(serializer.data)
    # --------------------------------------------------------------------------
    def update(self, request, *args, **kwargs):
        obj = self.get_object()
        hexcolor = request.data['hexcolor']
        # if (not obj.mvcolor) or obj.concept == "":
        obj.hexcolor = hexcolor
        obj.save()
        # else:
        #     rc_list = RangeColor.objects.filter(concept=obj.concept)
        #     for rc in rc_list:
        #         rc.hexcolor = hexcolor
        #         rc.save()

        serializer = RangeColorSerializer(RangeColor.objects.all(), many=True)
        return Response(serializer.data)
    # --------------------------------------------------------------------------
    def get_queryset(self): #this method is called inside of get
        queryset = RangeColor.objects.all()
        return queryset
# ==============================================================================
class MVColorEncodingViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.AllowAny] 
    serializer_class = MVColorEncodingSerializer
    # --------------------------------------------------------------------------
    def get_queryset(self): #this method is called inside of get
        queryset = MVColorEncoding.objects.all()
        return queryset
# ==============================================================================
class MVConceptGroupingViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.AllowAny] 
    serializer_class = MVConceptGroupingSerializer
    # --------------------------------------------------------------------------
    def get_queryset(self): #this method is called inside of get
        queryset = MVConceptGrouping.objects.all()
        return queryset
# ==============================================================================