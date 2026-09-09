import json
from core.apitools import *

print("Getting access token...")
access_token = get_access_token()
print("Access token obtained successfully.")

print("Getting project list...")
projects = get_projects(access_token)['iTwins']
print("Project list obtained successfully.")

project = projects[0]

schedules = get_schedules(access_token, project['id'])['schedules']

schedule = schedules[0]
