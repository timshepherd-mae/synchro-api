from core.api_auth import get_access_token
from core.api_itwins import get_projects
from core.outtools import print_records

print("Getting access token...")
access_token = get_access_token()
print("Access token obtained successfully.")

print("Getting project list...")
projects = get_projects(access_token)['iTwins']
print("Project list obtained successfully.")

print_records(projects)
