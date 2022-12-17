import numpy as np
from PIL import Image
from matplotlib import cm
import numpy as np
import warnings

from dxtbx.imageset import ImageSetFactory
import streamlit as st

BIN_RATIO = 6
CMAP = cm.magma #cm.gray_r

#warnings.filterwarnings(action='ignore', message='Mean of empty slice')
np.seterr(divide='ignore', invalid='ignore')

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
image_path = '/nfs/chess/daq/current/id7b2/meisburger/20221204/dose_test/lys1_sweep1_1_master.h5'
#image_path = '/nfs/chess/daq/current/id7b2/meisburger/20221204/align/snap_99_000013_master.h5'

with st.sidebar:
    frame = st.number_input('frame',min_value=0, max_value=200, value=0)
    b = load_and_rebin_masked(image_path,frame,[BIN_RATIO,BIN_RATIO])
    vmax = st.slider('maximum',0,200,value=50)

im = to_pil(b,CMAP,0,vmax)
st.image(im,use_column_width='never',caption=f'{image_path}:{frame}')
