from django.shortcuts import render


def dashboard(request):
    return render(request, "dashboard.html")

def cropping(request):
    return render(request, "pages/advanced-ui/cropper.html")