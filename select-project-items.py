import json
from core.apitools import *

print("Getting access token...")
access_token = get_access_token()
print("Access token obtained successfully.")

print("Getting project list...")
projects = get_projects(access_token)['iTwins']
print("Project list obtained successfully.")

selected = select_items([p["displayName"] for p in projects], title=None)

print(str(selected))