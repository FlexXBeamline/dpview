import numpy as np
from PIL import Image
from matplotlib import cm
import numpy as np
import warnings
import os
import glob

from dxtbx.imageset import ImageSetFactory
import streamlit as st
#import plotly.express as px

BIN_RATIO = 6
CMAP = cm.magma #cm.gray_r

#warnings.filterwarnings(action='ignore', message='Mean of empty slice')
np.seterr(divide='ignore', invalid='ignore')

def find_images():
    image_files = glob.glob('**/*_master.h5',recursive=True)
    return image_files
    #a = {}
    #for f in image_files:
#        name = f.replace('_master.h5','')
#        a[name] =
#    return a

@st.cache
def import_iset(fname):
    isets = ImageSetFactory.new(image_path)
    return isets[0] # assumes only one

@st.cache
def load_frame(fname,index):
    iset = import_iset(fname)
    arr = iset.get_raw_data(index)[0].as_numpy_array()
    msk = iset.get_mask(index)[0].as_numpy_array()
    return arr, msk

@st.cache
def load_and_rebin_masked(fname,index,bins):
    arr, msk = load_frame(fname,index)
    nbins = np.floor(arr.shape/np.array(bins)).astype(int)
    arr = arr[:nbins[0]*bins[0],:nbins[1]*bins[1]]
    msk = msk[:nbins[0]*bins[0],:nbins[1]*bins[1]]
    sh = nbins[0],bins[0],nbins[1],bins[1]
    return arr.reshape(sh).mean(axis=(1,3),where=msk.reshape(sh))

def to_pil(arr,cmapfun,vmin,vmax):
    return Image.fromarray(np.uint8(cmapfun((arr-vmin)/(vmax-vmin))*255))

#image_path = '/nfs/chess/daq/current/id7b2/meisburger/20221204/cut/lys3_sweep1_1_master.h5'
#image_path = '/nfs/chess/daq/current/id7b2/meisburger/20221204/dose_test/lys1_sweep1_1_master.h5'
#image_path = '/nfs/chess/daq/current/id7b2/meisburger/20221204/align/snap_99_000013_master.h5'

with st.sidebar:
    os.chdir(st.session_state.workdir)
    image_path = st.selectbox('Image Path',index=0,options=find_images())
    #image_path = st.text_input("Image Path",value="/Users/spm82/tmp/20221204/align/snap_99_000013_master.h5")
    frame = st.number_input('frame',min_value=0, max_value=200, value=0)
    b = load_and_rebin_masked(image_path,frame,[BIN_RATIO,BIN_RATIO])
    vmax = st.slider('maximum',0,200,value=50)

#fig = px.imshow(b,aspect='equal',zmin=0,zmax=vmax)
#st.plotly_chart(fig)
im = to_pil(b,CMAP,0,vmax)
st.image(im,use_column_width='never',caption=f'{image_path}:{frame}')
