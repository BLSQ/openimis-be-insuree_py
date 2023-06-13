import json
from django.http import HttpResponse
from .tasks import hera_life_event_handler


def ecrvs_webhook(request):
    print("ecrvs_webhook")
    data = json.loads(request.body.decode("utf-8"))
    hera_life_event_handler(data["nin"], data["context"])
    return HttpResponse("ok")
