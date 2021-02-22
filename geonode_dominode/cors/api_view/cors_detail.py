import datetime
import os
from django.http import (
    JsonResponse, HttpResponseBadRequest, HttpResponse, HttpResponseForbidden
)
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from cors.models.station import CORSStation


class CorsObservationDownloadDetail(APIView):
    """ Check download detail  """
    permission_classes = [IsAuthenticated]

    def post(self, request, id, format=None):
        data = request.data
        station = get_object_or_404(CORSStation, id=id)
        if not request.user.has_perm('cors.download_observation'):
            return HttpResponseForbidden()
        try:
            date_from = datetime.datetime.strptime(data['from'], '%Y-%m-%d')
            date_to = datetime.datetime.strptime(data['to'], '%Y-%m-%d')
            if date_from > date_to:
                return HttpResponseBadRequest('From is larger than to')
            return JsonResponse({
                'filesize': station.indexes_size(date_from, date_to),
                'filename': station.indexes_in_zip_filename(date_from, date_to)
            })
        except KeyError as e:
            return HttpResponseBadRequest('{} is required'.format(e))


class CorsObservationDownload(APIView):
    """ Download cors observation in date range """
    permission_classes = [IsAuthenticated]

    def post(self, request, id, format=None):
        data = request.data
        station = get_object_or_404(CORSStation, id=id)
        if not request.user.has_perm('cors.download_observation'):
            return HttpResponseForbidden()
        try:
            date_from = datetime.datetime.strptime(data['from'], '%Y-%m-%d')
            date_to = datetime.datetime.strptime(data['to'], '%Y-%m-%d')
            if date_from > date_to:
                return HttpResponseBadRequest('From is larger than to')
            path = station.indexes_in_zip(date_from, date_to)
            with open(path, 'rb') as zip_file:
                response = HttpResponse(zip_file.read(), content_type="application/zip")
                response['Content-Disposition'] = 'attachment; filename="%s"' % os.path.basename(path)
                return response
        except KeyError as e:
            return HttpResponseBadRequest('{} is required'.format(e))
