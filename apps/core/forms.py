from django import forms
from .models import Image

class ImageForm(forms.ModelForm):
    class Meta:
        model = Image
        fields = ['original_image', 'width', 'height']

from django import forms
from .models import Image

class ImageSegmentationForm(forms.ModelForm):
    threshold = forms.IntegerField()

    class Meta:
        model = Image
        fields = ['original_image', 'threshold']
        
class EdgeBasedSegmentationForm(forms.ModelForm):
    class Meta:
        model = Image
        fields = ['original_image']
