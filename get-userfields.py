import json
from pathlib import Path
from core.apitools import *
from core.outtools import *

print()
print("*** Getting access token...")
access_token = get_access_token()
print("*** Access token obtained successfully.")

print("*** Getting project list...")
projects = get_projects(access_token)['iTwins']
print("*** Project list obtained successfully.")

print_records(projects, n=15)

project = projects[0]

print("*** Getting schedules from Project=0...")
schedules = get_schedules(access_token, project['id'])['schedules']
print("*** Schedules obtained successfully.")

print_records(schedules, n=15)

schedule = schedules[0]

print("*** Getting user fields from Schedule=0...")
user_fields = get_all_userfields(access_token, schedule['id'])
print("*** User fields obtained successfully.")


output_file = compile_filename(
    uptree=1,
    destination="data_export/test_export",
    filename="userfields"
)


user_fields_out = save_response_records(
    records=user_fields,
    filename=output_file,
    filetype=FILETYPE_CSV
)

print_records(user_fields, n=15)