#!/usr/bin/env python3
"""Explicit synthetic-fixture screening, NOT proof of physical sensor origin.

Run before treating an Adaptive Cooling CSV as bench evidence. This narrow
preflight does not replace the timestamp, energy, uncertainty or safety audit.
"""
import argparse
import csv
import json
from pathlib import Path

RAW_HEADER = 'run_id,timestamp,condition,ambient_temp_c,ambient_rh_pct,target_temp_c,target_rh_pct,air_velocity_m_s,surface_temp_c,power_w,energy_wh,condensation_flag,notes'.split(',')
INSTRUMENT_HEADER = 'instrument_id,measurement,make_model,range,accuracy_or_uncertainty,resolution,sampling_interval_s,calibration_or_check_method,last_check_date,placement_or_geometry,notes'.split(',')
REQUIRED = {'ambient_temperature','ambient_relative_humidity','target_zone_temperature','target_zone_relative_humidity','air_velocity','surface_temperature','electrical_power','electrical_energy'}
PROVENANCE = ('instrument_id','make_model','accuracy_or_uncertainty','calibration_or_check_method','last_check_date','placement_or_geometry')
MARKERS = ('FICTIONAL','SYNTHETIC','SIMULATED','MOCK')
UNKNOWN = {'','TBD','UNKNOWN','N/A','NA','NONE'}


def marked(value):
    return any(word in str(value).upper() for word in MARKERS)


def read_table(path, expected, problems, label):
    try:
        with Path(path).open(encoding='utf-8-sig', newline='') as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames != expected:
                problems.append(label+'_HEADER')
                return []
            rows = list(reader)
            if any(None in row or None in row.values() for row in rows):
                problems.append(label+'_ROW')
            return [row for row in rows if None not in row and None not in row.values()]
    except (OSError, UnicodeError, csv.Error):
        problems.append(label+'_READ')
        return []


def check(raw_path, manifest_path, plan_path, mode='bench'):
    if mode not in ('bench','dry-run'):
        raise ValueError('mode must be bench or dry-run')
    problems=[]
    raw=read_table(raw_path, RAW_HEADER, problems, 'RAW')
    instruments=read_table(manifest_path, INSTRUMENT_HEADER, problems, 'INSTRUMENT')
    try:
        plan=json.loads(Path(plan_path).read_text(encoding='utf-8'))
    except (OSError, UnicodeError, json.JSONDecodeError):
        plan={}
        problems.append('PLAN_READ')
    if not isinstance(plan,dict):
        plan={}
        problems.append('PLAN_OBJECT')
    if not raw:
        problems.append('RAW_EMPTY')
    if mode=='bench':
        if marked(json.dumps(plan,sort_keys=True)):
            problems.append('EXPLICIT_FICTIONAL_PLAN')
        if any(marked(value) for row in raw for value in row.values()):
            problems.append('EXPLICIT_FICTIONAL_RAW')
        if any(marked(value) for row in instruments for value in row.values()):
            problems.append('EXPLICIT_FICTIONAL_INSTRUMENT')
        counts={key:0 for key in REQUIRED}
        for row in instruments:
            name=row.get('measurement')
            if name in counts:
                counts[name]+=1
                if any(str(row.get(key,'')).strip().upper() in UNKNOWN for key in PROVENANCE):
                    problems.append('INSTRUMENT_PROVENANCE_TBD')
        if any(n!=1 for n in counts.values()):
            problems.append('INSTRUMENT_COVERAGE')
        if any(str(plan.get(key,'')).strip().upper() in UNKNOWN for key in
               ('geometry_id','ambient_position','target_position','surface_position','power_boundary')):
            problems.append('GEOMETRY_TBD')
    return {'mode':mode,'status':'REJECTED' if problems else 'STRUCTURE_ONLY_ORIGIN_UNVERIFIED',
            'problems':sorted(set(problems)),'raw_rows':len(raw),
            'physical_origin_authenticated':False,'performance_claim_permitted':False}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--raw',required=True)
    parser.add_argument('--manifest',required=True)
    parser.add_argument('--plan',required=True)
    parser.add_argument('--mode',choices=['bench','dry-run'],default='bench')
    args=parser.parse_args()
    result=check(args.raw,args.manifest,args.plan,args.mode)
    print(json.dumps(result,sort_keys=True,indent=2))
    raise SystemExit(2 if result['status']=='REJECTED' else 0)

if __name__=='__main__':
    main()
