from django.http import JsonResponse
from rest_framework.views import APIView


class CorsList(APIView):
    """ Return cors list as geojson """
    permission_classes = []

    def get(self, request, format=None):
        example = {
            "type": "FeatureCollection",
            "features": [{
                "type": "Feature",
                "properties": {
                    "ID": 1,
                    "Status": "Operational",
                    "Sampling Rate": "30 sec(s)",
                    "Availability": "Hourly",
                    "GNSS": "GPS+GLO",
                    "Agency": "Institut Geographique National - France"
                },
                "geometry": {
                    "type": "Point",
                    "coordinates": [-61.388993, 15.2997062]
                }
            }]
        }
        return JsonResponse(example)
