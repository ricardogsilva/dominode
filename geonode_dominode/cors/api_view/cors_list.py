from django.http import JsonResponse
from rest_framework.views import APIView
from cors.models.station import CORSStation


class CorsList(APIView):
    """ Return cors list as geojson """
    permission_classes = []

    def get(self, request, format=None):
        example = {
            "type": "FeatureCollection",
            "features": [{
                "type": "Feature",
                "properties": {
                    "ID": station.id,
                    "Name": station.name,
                    "Elevation": station.z,
                },
                "geometry": {
                    "type": "Point",
                    "coordinates": [station.y, station.x]
                }
            } for station in CORSStation.objects.all()]
        }
        return JsonResponse(example)
