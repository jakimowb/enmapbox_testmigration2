

import typing
import pathlib
import json
import datetime

PATH_DB_JSON = pathlib.Path(r'C:\Users\geo_beja\Downloads\enmap-box-issues\db-2.0.json')

assert PATH_DB_JSON.is_file(), 'No json, no stats!'

start_date = datetime.date(2020, 7, 1)
end_date = datetime.date(2020, 12, 31)


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

s = ""