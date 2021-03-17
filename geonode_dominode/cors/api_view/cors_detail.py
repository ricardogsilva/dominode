import datetime
import os
from django.http import (
    JsonResponse, HttpResponseBadRequest, HttpResponse, HttpResponseForbidden
)
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from cors.models.station import CORSStation
from django.shortcuts import render
from django.conf import settings

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
                'filename': station.indexes_in_txt_filename(date_from, date_to)
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
            path = station.indexes_in_txt(date_from, date_to)
            indexes = station.get_indexes(date_from, date_to)
            context = {
                   'indexes': indexes,
                   'SITE_URL': settings.SITEURL
              }
            return render(request, 'cors/table.html', context)
        except KeyError as e:
            return HttpResponseBadRequest('{} is required'.format(e))
