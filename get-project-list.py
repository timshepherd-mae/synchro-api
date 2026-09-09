import json
from core.apitools import *

print("Getting access token...")
access_token = get_access_token()
print("Access token obtained successfully.")

print("Getting project list...")
projects = get_projects(access_token)['iTwins']
print("Project list obtained successfully.")

print()
print()
print(build_string_table(projects, fields=None, padding=5))
print()
print()
