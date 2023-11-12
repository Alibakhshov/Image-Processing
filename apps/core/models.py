from django.db import models

from django.db import models

class Image(models.Model):
    original_image = models.ImageField(upload_to='images/')
    resized_image = models.ImageField(upload_to='resized_images/', blank=True, null=True)
    width = models.IntegerField(blank=True, null=True)
    height = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    
    def __str__(self):
        return f'Image {self.pk}' 