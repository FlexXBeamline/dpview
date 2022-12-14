import os

import streamlit as st

st.title('Settings')

# callback for form submission
def update_settings():
    st.session_state.workdir = st.session_state.base_directory_input

# make the form
with st.form(key='settings'):
    st.text_input("Base Directory",
        key='base_directory_input',
        value=st.session_state.workdir)
    submit = st.form_submit_button(label='Update', on_click=update_settings)

#st.write(st.session_state)
