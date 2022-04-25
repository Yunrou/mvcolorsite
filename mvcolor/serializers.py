from rest_framework import serializers
from .models import Dataset, Chart, ColorEncoding, Color, \
                    ColorScheme, ColorConfig, Parameter, Example,\
                    RangeColor, MVColorEncoding, MVConceptGrouping

# Turn our model into serializer
class ChartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chart
        fields = "__all__"

class ColorEncodingSerializer(serializers.ModelSerializer):
    class Meta:
        model = ColorEncoding
        fields = "__all__"

class RangeColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = RangeColor
        fields = "__all__"

class DatasetSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        print(validated_data)
        return Dataset.objects.create(**validated_data)
    class Meta:
        model = Dataset
        fields = ('name',)
        
class ColorSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        print(validated_data)
        return Color.objects.create(**validated_data)
    class Meta:
        model = Color
        fields = "__all__"

class ColorSchemeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ColorScheme
        fields = ('name',)

class ColorConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = ColorConfig
        fields = "__all__"
        
class ParameterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parameter
        fields = "__all__"

class ExampleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Example
        fields = "__all__"

class MVColorEncodingSerializer(serializers.ModelSerializer):
    class Meta:
        model = MVColorEncoding
        fields = "__all__"

class MVConceptGroupingSerializer(serializers.ModelSerializer):
    class Meta:
        model = MVConceptGrouping
        fields = "__all__"