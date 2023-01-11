import json
import glob
import os
from collections import UserDict

import streamlit as st
import pandas as pd

DEFAULT_SETTINGS = {'workdir':os.getcwd()}

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
    'autoindex_inp':'AUTOINDEX.INP',
    }

STATUS_LABELS = {
    'complete':':heavy_check_mark:',
    'error':':interrobang:',
    'working':':thought_balloon:',
}

st.set_page_config(layout="wide")

# keep settings synchronized with the URL parameters
class Settings(UserDict):
    def __init__(self,defaults):
        url_params = st.experimental_get_query_params()
        for k in url_params:
            defaults[k] = url_params[k][0]
        super().__init__(defaults)

    def __setitem__(self,key,value):
        super().__setitem__(key,value)
        st.experimental_set_query_params(**self)

settings = Settings(DEFAULT_SETTINGS)

# make the form
with st.sidebar:

    st.title('DPVIEW')
    st.write('View results of automated data processing (fast_dp)')
    st.header('Settings')

    def update_settings():
        settings['workdir'] = st.session_state.base_directory_input

    st.text_input('Base Directory',
        key='base_directory_input',
        value=settings['workdir'],
        on_change=update_settings)

    st.button('refresh')

os.chdir(settings['workdir'])

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

st.write('todo: select dataset and load all files')

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
