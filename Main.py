import json
import glob
import os

import streamlit as st

st.set_page_config(layout="wide")

# apply default settings
if 'workdir' not in st.session_state:
    #st.write('default settings applied')
    st.session_state.workdir = os.getcwd()

st.title('DPVIEW')

st.write('View results of automated data processing (fast_dp)')
