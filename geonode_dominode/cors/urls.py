# -*- coding: utf-8 -*-
#########################################################################
#
# Copyright (C) 2017 OSGeo
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
#########################################################################

from django.conf.urls import url, include
from cors.api_view.cors_list import CorsList
from cors.api_view.cors_detail import CorsObservationDownload, CorsObservationDownloadDetail
from cors.views import MapView

API = [
    url(r'^list',
        view=CorsList.as_view(),
        name='cors-list'),
    url(r'^(?P<id>\d+)/observation/download/detail',
        view=CorsObservationDownloadDetail.as_view(),
        name='cors-observation-download-detail'),
    url(r'^(?P<id>\d+)/observation/download',
        view=CorsObservationDownload.as_view(),
        name='cors-observation-download'),
]
urlpatterns = [
    url(r'^map/?$',
        MapView.as_view(),
        name='cors-map'),
    url(r'^api/', include(API)),
]
