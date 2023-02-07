from django.http import HttpResponse
from django.shortcuts import render

import sys
sys.path.append("../backend")
from main import TextValidate

TEXTVALIDATE_CLASS = TextValidate()

# Create your views here.
def home_view(request, *args, **kwargs):
    models = {

    }
    return render(request, "base.html", models)

def evaluation_view(request, *args, **kwargs):
    text = request.POST["text"]
    validated_text = TEXTVALIDATE_CLASS.main(text)
    
    context = {
        "input_text" : text,
        "validated" : validated_text
    }
    return render(request, "base.html", context)
