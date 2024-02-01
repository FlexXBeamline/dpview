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

# column names
CELL, SG, DS = 'Unit Cell', 'Space Group', 'Dataset'
COMP, MULT = 'Completeness', 'Multiplicity'
ISIGI, RESOL, RMERGE = 'I/σI', 'Resolution', 'Rmerge'

# columns in order
COLUMNS = [DS, SG, CELL, RESOL, ISIGI, COMP, MULT, RMERGE]

st.set_page_config(layout="wide")

with st.sidebar:

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
    fast_dp_folders = glob.glob('**/*fast_dp/',recursive=True)
    a = {}
    for f in fast_dp_folders:
        b = {v:os.path.join(f,v) for v in LOG_FILES if os.path.exists(os.path.join(f,v))}
        fname = f.replace('_fast_dp/','').replace('fast_dp/','') # covers legacy folder names
        a[fname] = b
    return a

def parse_fast_dp_results(fast_dp):
    """convert dictionary from fast_dp.json to dict with standard keys"""

    results = {k:None for k in COLUMNS}
    results[CELL] = fast_dp.get('unit_cell',None),
    results[SG] = fast_dp.get('spacegroup',None),
    results[DS] = fast_dp.get('data',None)
    
    if 'scaling_statistics' in fast_dp: # new version
        stats = fast_dp['scaling_statistics'].get('overall',{})
        
        results[COMP] = stats.get('completeness',None)
        results[MULT] = stats.get('multiplicity',None)
        results[ISIGI] = stats.get('mean_i_sig_i',None)
        results[RESOL] = stats.get('res_lim_high',None)
        results[RMERGE] = stats.get('r_merge',None)
        
    elif 'xml_results' in fast_dp: # old version
        stats = fast_dp['xml_results']
        
        results[COMP] = stats.get('completeness_overall',None)
        results[MULT] = stats.get('multiplicity_overall',None)
        results[ISIGI] = stats.get('isigma_overall',None)
        results[RESOL] = stats.get('resol_high_overall',None)
        results[RMERGE] =stats.get('rmerge_overall',None)
        
    else: # not recognized
        pass
        
    return results


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
    fast_dp = parse_fast_dp_results(fast_dp)
    a.append(fast_dp)
    
if len(a)==0:
    st.warning('No fast_dp folders found in directory.')
    st.stop()

df = pd.json_normalize(a)
print(df)

df = df[COLUMNS]

gb = GridOptionsBuilder.from_dataframe(df)
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
    dataset = selected[0][DS]
    st.header(dataset)
    for k,v in s[dataset].items():
        with st.expander(k,expanded=False):
            with open(v) as f:
                st.text(f.read())
