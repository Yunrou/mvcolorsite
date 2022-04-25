from django.apps import AppConfig
import sys, os
from django.conf import settings

class MvcolorConfig(AppConfig):
    name = 'mvcolor'

    def ready(self):
        if 'runserver' not in sys.argv:
            return True
        # you must import your modules here 
        # to avoid AppRegistryNotReady exception 
        from .models import ColorScheme, Color, Dataset, Chart, \
                            ColorConfig, Parameter, Example, \
                            ColorEncoding, RangeColor, MVColorEncoding, \
                            MVConceptGrouping

        from .src.load_example import load_example

        Dataset.objects.all().delete()
        Chart.objects.all().delete()
        ColorEncoding.objects.all().delete()
        RangeColor.objects.all().delete()
        ColorScheme.objects.all().delete()
        Color.objects.all().delete()
        ColorConfig.objects.all().delete()
        Parameter.objects.all().delete()
        Example.objects.all().delete()
        MVColorEncoding.objects.all().delete()
        MVConceptGrouping.objects.all().delete()

        # Initialize
        obj = ColorConfig.objects.create(name='user', 
                                         bgcolor='#ffffff',#'#f3f2f4', 
                                         textcolor='#333333')
        obj = Parameter.objects.create(name='user',
                                       min_n_color=1,
                                       max_n_color=9,
                                       gamma=0.3,
                                       consistency='visual+semantics',
                                       mvce_id=0,
                                       mvcg_pk=0,
                                       isTheme=True)
        # Initialize colorscheme
        from .src.util.colorschemes import colorschemes

        for k, v in colorschemes.items():
            obj = ColorScheme.objects.create(name=k)
            if k == 'tableau10':
                for color in v:
                    obj1 = Color.objects.create(color=color, colorscheme='user')
                    obj2 = Color.objects.create(color=color, colorscheme='tableau10')
            else:
                for color in v:
                    obj = Color.objects.create(color=color, colorscheme=k)

        # Create example objects
        example_root = os.path.join(settings.MEDIA_ROOT, 'example')
        examples = sorted(os.listdir(example_root))
        for filename in examples:
            if filename[0] == '.': continue 
            if filename[0] in ('0'): continue
            name = ' '.join(filename.split('_'))
            obj = Example.objects.create(name=name, value=filename,
                                         current=False)
            # Load examples
            # for the first time: set save_mvobject to True (save the model.sav)
            if filename[0] in ('3', '4', '5'):
                # load_example(filename, save_mvobject=True)
                load_example(filename, save_mvobject=False)