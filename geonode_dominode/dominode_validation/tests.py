from django.test import TestCase

# Create your tests here.

# TODO: write some basic integration tests

# workflow from the client shall be:
#
# 1. check if the resource exists by GETting `/dominode-validaton/api/dominode-resources/?name={name}`
# 2. if resource does not exist, create it by POSTing to `/dominode-validaton/api/dominode-resources/`
# 3. POST a new report to `/dominode-validaton/api/validation-reports/`
#
# use django authentication for the api requests

# sample POST request to `/dominode-validaton/api/dominode-resources/`
#
# {
#     "name": "ppd_roads_v1.0.0",
#     "resource_type": "vector",
#     "artifact_type": "dataset"
# }

# sample POST request to `/dominode-validaton/api/validation-reports/`
#
# {
#     "resource": "ppd_roads_v1.0.0",
#     "result": true,
#     "validator": "admin",
#     "validation_datetime": "2020-09-22T00:00:04",
#     "checklist_name": "dummy",
#     "checklist_description": "my fake checklist",
#     "checklist_steos": null
# }
