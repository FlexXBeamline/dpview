import json
import glob
import os

import streamlit as st
import pandas as pd

FAST_DP_JSON_TO_COLS = {
    'xml_results.completeness_overall':'completeness',
    'xml_results.multiplicity_overall':'multiplicity',
    'xml_results.isigma_overall':'I/σI',
    'xml_results.resol_high_overall':'resolution',
    'xml_results.rmeas_overall':'Rmeas',
    }

DISPLAY_COLS = [
    "unit_cell",
    "spacegroup",
    "resolution",
    "completeness",
    "multiplicity",
    "I/σI",
    "Rmeas",
    ]

LOG_FILES = {
    'fast_dp_json':'fast_dp.json',
    'fast_dp_log':'fast_dp.log',
    'fast_dp_error':'fast_dp.error',
    'fast_dp_state':'fast_dp.state',
    'autoindex_log':'autoindex.log',
    }

STATUS_LABELS = {
    'complete':':heavy_check_mark:',
    'error':':interrobang:',
    'working':':thought_balloon:',
}

#if 'workdir' not in st.session_state:
#    st.session_state['workdir'] = os.getcwd()

os.chdir(st.session_state.workdir)

st.title('Data processing results')
st.button('refresh')
#st.write(st.session_state.workdir)

def find_fast_dp_folders():
    fast_dp_folders = glob.glob('**/*_fast_dp/',recursive=True)
    a = {}
    for f in fast_dp_folders:
        b = {k:os.path.join(f,v) for k,v in LOG_FILES.items() if os.path.exists(os.path.join(f,v))}
        a[f.replace('_fast_dp/','')] = b
    return a

st.header('Summary statistics')

s = find_fast_dp_folders()

# get fast_dp status
for k in s:
    if 'fast_dp_json' in s[k]:
        s[k]['status'] = 'complete'
    elif 'fast_dp_error' in s[k]:
        s[k]['status'] = 'error'
    else:
        s[k]['status'] = 'working'

a = []
for k in s:
    if 'fast_dp_json' in s[k]:
        with open(s[k]['fast_dp_json']) as f:
            fast_dp = json.load(f)
    else:
        fast_dp = {}
    fast_dp['data'] = k
    a.append(fast_dp)

df = pd.json_normalize(a)
df.set_index('data', inplace = True)
df.sort_index(inplace = True)
df.rename(columns=FAST_DP_JSON_TO_COLS, inplace = True)

st.write(df[DISPLAY_COLS])

st.header('Log files')

for k in sorted(s):
    label = k
    if s[k]['status'] in STATUS_LABELS:
        label += ' ' + STATUS_LABELS[s[k]['status']]
    with st.expander(label,expanded=False):
        if 'fast_dp_error' in s[k]:
            with open(s[k]['fast_dp_error']) as f:
                st.error(f.read())
        if 'fast_dp_log' in s[k]:
            with open(s[k]['fast_dp_log']) as f:
                st.text(f.read())
        else:
            st.write('log file not found')
