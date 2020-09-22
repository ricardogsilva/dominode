import datetime
from django.http import (
    JsonResponse, HttpResponseBadRequest, HttpResponse, HttpResponseForbidden
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView


class CorsDetail(APIView):
    """ Return cors detail as json """
    permission_classes = []

    def get(self, request, id, format=None):
        example = {
            "type": "Feature",
            "id": 1,
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
        }
        return JsonResponse(example)


class CorsObservationDownloadDetail(APIView):
    """ Check download detail  """
    permission_classes = [IsAuthenticated]

    def post(self, request, id, format=None):
        data = request.data
        if not request.user.has_perm('cors.download_observation'):
            return HttpResponseForbidden()
        try:
            date_from = datetime.datetime.strptime(data['from'], '%Y-%m-%d')
            date_to = datetime.datetime.strptime(data['to'], '%Y-%m-%d')
            if date_from > date_to:
                return HttpResponseBadRequest('From is larger than to')
            return JsonResponse({
                'filesize': '1000MB',
                'filename': 'test'
            })
        except KeyError as e:
            return HttpResponseBadRequest('{} is required'.format(e))


class CorsObservationDownload(APIView):
    """ Download cors observation in date range """
    permission_classes = [IsAuthenticated]

    def post(self, request, id, format=None):
        data = request.data
        if not request.user.has_perm('cors.download_observation'):
            return HttpResponseForbidden()
        try:
            date_from = datetime.datetime.strptime(data['from'], '%Y-%m-%d')
            date_to = datetime.datetime.strptime(data['to'], '%Y-%m-%d')
            if date_from > date_to:
                return HttpResponseBadRequest('From is larger than to')

            # download
            # Create and return response with created pdf
            response = HttpResponse('OK')
            response['Content-Type'] = 'application/pdf'
            response['Content-disposition'] = 'attachment ; filename = {}'.format('test')
            return response
        except KeyError as e:
            return HttpResponseBadRequest('{} is required'.format(e))
