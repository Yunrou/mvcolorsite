from django.contrib import admin
from .models import Dataset, Chart, Color, ColorScheme, \
                    ColorConfig, Parameter, ColorEncoding, \
                    RangeColor, Example, MVColorEncoding, MVConceptGrouping

# Register your models here.
admin.site.register(Dataset)
admin.site.register(Chart)
admin.site.register(Color)
admin.site.register(ColorScheme)
admin.site.register(ColorConfig)
admin.site.register(Parameter)
admin.site.register(ColorEncoding)
admin.site.register(RangeColor)
admin.site.register(Example)
admin.site.register(MVColorEncoding)
admin.site.register(MVConceptGrouping)