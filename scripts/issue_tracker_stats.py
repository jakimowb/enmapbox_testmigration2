

import typing
import pathlib
import json
import datetime
import csv
# 1. open bitbucket,
# goto repository settings -> issues
# 2. export issues, extract zip file and copy db-2.0.json to JSON_DIR (defaults to <repo>/tmp)
# 3. set report period with start_date / end_date
JSON_DIR = pathlib.Path(__file__).parents[1] / 'tmp'
start_date = datetime.date(2020, 10, 29)
end_date = datetime.date(2021, 3, 15)



PATH_DB_JSON = JSON_DIR / 'db-2.0.json'
PATH_REPORT = JSON_DIR / 'issue_report.csv'
assert PATH_DB_JSON.is_file(), 'No db-2.0.json, no stats!'
assert start_date < end_date
with open(PATH_DB_JSON, 'r', encoding='utf-8') as f:
    DB = json.load(f)

ISSUES = DB['issues']

CREATED_ISSUES = [i for i in ISSUES if start_date
                  <= datetime.datetime.fromisoformat(i['created_on']).date()
                  <= end_date]
UPDATED_ISSUES = [i for i in ISSUES if start_date
                  <= datetime.datetime.fromisoformat(i['updated_on']).date()
                  <= end_date]

def byKey(ISSUES:list, key:str) -> dict:
    R = dict()
    for issue in ISSUES:
        k = issue[key]
        L = R.get(k, [])
        L.append(issue)
        R[k] = L
    return R

CREATED_BY_STATUS = byKey(CREATED_ISSUES, 'status')
UPDATED_BY_STATUS = byKey(UPDATED_ISSUES, 'status')

print(f'Created: {len(CREATED_ISSUES)}')
for k in sorted(CREATED_BY_STATUS.keys()):
    print(f'\t{k}: {len(CREATED_BY_STATUS[k])}')

print(f'Updated: {len(UPDATED_ISSUES)}')
for k in sorted(UPDATED_BY_STATUS.keys()):
    print(f'\t{k}: {len(UPDATED_BY_STATUS[k])}')

with open(PATH_REPORT, 'w', encoding='utf-8', newline='') as f:
    states = ['new', 'open', 'on hold', 'resolved', 'closed', 'duplicate', 'wontfix', 'invalid']
    fieldnames = ['action', 'total'] + states
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    total_created = total_updated = 0
    ROW1 = {'action': 'created'}
    ROW2 = {'action': 'updated'}

    for s in states:
        total_created += len(CREATED_BY_STATUS.get(s, 0))
        total_updated += len(UPDATED_BY_STATUS.get(s, 0))
        ROW1[s] = len(CREATED_BY_STATUS[s])
        ROW2[s] = len(UPDATED_BY_STATUS[s])
    ROW1['total'] = total_created
    ROW2['total'] = total_updated
    writer.writerow(ROW1)
    writer.writerow(ROW2)

