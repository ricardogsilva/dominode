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

# sample POST request to `/dominode-validaton/api/validation-reports/`
#
# {
#     "resource": "ppd_roads_v1.0.0",
#     "result": true,
#     "report": {},
#     "validator": "admin"
# }
