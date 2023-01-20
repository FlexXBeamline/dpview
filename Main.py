import json
import glob
import os
from collections import UserDict

import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder

LOG_FILES = [
    'fast_dp.error',
    'fast_dp.json',
    'fast_dp.log',
    'autoindex.log',
    ]

COLUMN_NAMES = {
    "unit_cell":"Unit Cell",
    "spacegroup":"Space Group",
    "data":"Dataset",
    'xml_results.completeness_overall':'Completeness',
    'xml_results.multiplicity_overall':'Multiplicity',
    'xml_results.isigma_overall':'I/σI',
    'xml_results.resol_high_overall':'Resolution',
    'xml_results.rmeas_overall':'Rmeas',
}

# columns to include, and the order to include them in
COLUMNS = [
    'data',
    'spacegroup',
    'unit_cell',
    'xml_results.resol_high_overall',
    'xml_results.isigma_overall',
    'xml_results.completeness_overall',
    'xml_results.multiplicity_overall',
    'xml_results.rmeas_overall',
]

st.set_page_config(layout="wide")

st.title('DPVIEW')
st.write('View results of automated data processing (fast_dp)')

def update_directory():
    try:
        os.chdir(st.session_state.base_directory_input)
    except:
        st.error('Directory does not exist, please enter a new one')

st.text_input('Base Directory',
    key='base_directory_input',
    value=os.getcwd(),
    on_change=update_directory)

st.button('refresh')

def find_fast_dp_folders():
    fast_dp_folders = glob.glob('**/*_fast_dp/',recursive=True)
    a = {}
    for f in fast_dp_folders:
        b = {v:os.path.join(f,v) for v in LOG_FILES if os.path.exists(os.path.join(f,v))}
        a[f.replace('_fast_dp/','')] = b
    return a

st.header('Summary statistics')
st.write('Select a row to view log files')

s = find_fast_dp_folders()

a = []
for k,v in s.items():
    if 'fast_dp.json' in v:
        with open(v['fast_dp.json']) as f:
            fast_dp = json.load(f)
    else:
        fast_dp = {}
    fast_dp['data'] = k
    a.append(fast_dp)

df = pd.json_normalize(a)

df = df[COLUMNS]

gb = GridOptionsBuilder.from_dataframe(df)
for k,v in COLUMN_NAMES.items():
    if k in COLUMNS:
        gb.configure_column(k, header_name=v)

gb.configure_selection('single',use_checkbox=False)
go = gb.build()

grid_response = AgGrid(
    df,
    gridOptions=go,
    fit_columns_on_grid_load=True,
    update_mode='SELECTION_CHANGED',
    )

selected = grid_response['selected_rows']

if selected:
    dataset = selected[0]['data']
    st.header(dataset)
    for k,v in s[dataset].items():
        with st.expander(k,expanded=False):
            with open(v) as f:
                st.text(f.read())
