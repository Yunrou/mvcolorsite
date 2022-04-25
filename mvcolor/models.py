from django.db import models
from django.urls import reverse, reverse_lazy
import os

# ==============================================================================
class Dataset(models.Model):
    example = models.CharField(max_length=100, default='')
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to='dataset/', max_length=500)
    # --------------------------------------------------------------------------
    def __str__(self):
        return self.name
# ==============================================================================
class ColorEncoding(models.Model):
    chart_id = models.IntegerField(default=0)
    ce_id = models.IntegerField(default=0)
    field = models.CharField(max_length=255, default='')
    name  = models.CharField(max_length=255, default='')
    vegalite = models.CharField(max_length=1000, default='')
# ==============================================================================
class RangeColor(models.Model):
    chart_id = models.IntegerField(default=0)
    ce_id = models.IntegerField(default=0)
    range_id = models.IntegerField(default=0)
    concept = models.CharField(max_length=100, default='')
    hexcolor = models.CharField(max_length=8, default='')
    mvcolor = models.BooleanField(default=False)
# ==============================================================================
class Chart(models.Model):
    current = models.BooleanField(default=False)
    example = models.CharField(max_length=100, default='')
    index = models.IntegerField(default=0)
    name = models.CharField(max_length=255)
    title = models.CharField(max_length=255, default='')
    file = models.FileField(upload_to='chart/', max_length=500)
    spec = models.CharField(max_length=5000)
    raw_spec = models.CharField(max_length=5000)
    dataset = models.CharField(max_length=255)
    ce_id = models.IntegerField(default=0)
    ce_field = models.CharField(max_length=500, default='')
    x = models.IntegerField(default=0)
    y = models.IntegerField(default=0)
    w = models.IntegerField(default=6)
    h = models.IntegerField(default=8)
    # --------------------------------------------------------------------------
    def __str__(self):
        return self.name
# ==============================================================================
class Color(models.Model):
    color = models.CharField(max_length=8)
    colorscheme = models.CharField(max_length=100)
    # --------------------------------------------------------------------------
    def __str__(self):
        return self.colorscheme+": "+self.color
# ==============================================================================
class ColorConfig(models.Model):
    name = models.CharField(max_length=100, default='')
    bgcolor = models.CharField(max_length=8)
    textcolor = models.CharField(max_length=8)
    # --------------------------------------------------------------------------
    def __str__(self):
        return "bgcolor: {}, textcolor: {}".format(self.bgcolor, self.textcolor)
# ==============================================================================
class ColorScheme(models.Model):
    name = models.CharField(max_length=100)
    # --------------------------------------------------------------------------
    def __str__(self):
        return self.name
# ==============================================================================
class Parameter(models.Model):
    name = models.CharField(max_length=100)
    min_n_color = models.IntegerField(default=1)
    max_n_color = models.IntegerField(default=9)
    gamma = models.FloatField(default=0.5)
    consistency = models.CharField(max_length=100, default='')
    mvce_id = models.IntegerField(default=0)
    mvcg_pk = models.IntegerField(default=0)
    isTheme = models.BooleanField(default=False)
# ==============================================================================
class Example(models.Model):
    name = models.CharField(max_length=100)
    value = models.CharField(max_length=100)
    current = models.BooleanField(default=False)
# ==============================================================================
class MVColorEncoding(models.Model):
    mvce_id = models.IntegerField(default=0)
    name = models.CharField(max_length=100)
    value = models.CharField(max_length=100)
# ==============================================================================
class MVConceptGrouping(models.Model):
    mvce_id = models.IntegerField(default=0)
    mvcg_id = models.IntegerField(default=0)
    name = models.CharField(max_length=100, default='')
    value = models.CharField(max_length=100, default='')
    consistency = models.CharField(max_length=100, default='')
# ==============================================================================
# class ColorAssignment(models.Model):
#     mvce_id = models.IntegerField(default=0)
#     mvcg_id = models.IntegerField(default=0)
#     ca_id   = models.IntegerField(default=0)
#     name = models.CharField(max_length=100, default='')
#     value = models.CharField(max_length=100, default='')
#     consistency = models.CharField(max_length=100, default='')
# ==============================================================================