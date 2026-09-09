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

print("*** Getting tasks from Schedule=0...")
tasks = get_all_tasks(access_token, schedule['id'])
print("*** Tasks obtained successfully.")


output_file = compile_filename(
    uptree=1,
    destination="data_export/test_export",
    filename="tasks"
)


tasks_out = save_response_records(
    records=tasks,
    filename=output_file,
    filetype=FILETYPE_CSV
)

print_records(tasks, n=15)