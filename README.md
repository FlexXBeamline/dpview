# dpview
quick viewer for fast_dp results

## Installation instructions

See: https://docs.streamlit.io/library/get-started/installation#install-streamlit-on-macoslinux

### Create a conda environment and install dependencies

```
conda create --name dpview python=3.9
conda activate dpview
conda install numpy pandas
pip install streamlit
pip install streamlit-aggrid
```

Test out the installation

```
streamlit hello
```

## Running dpview App

```
cd /path/to/user/data/directory
streamlit run /path/to/dpview/Main.py
```
