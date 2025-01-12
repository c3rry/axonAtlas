import numpy as np
import tifffile
import tempfile
import streamlit as st
import os
import matplotlib.cm as cm

@st.cache_data
def load_tiff(uploaded_file):
    with tempfile.NamedTemporaryFile(delete=False, suffix='.tif') as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        with tifffile.TiffFile(tmp_file.name) as tif:
            return tif.asarray()

def adjust_brightness(image, brightness_min, brightness_max, opacity=1.0):
    adjusted = np.clip(image, brightness_min, brightness_max)
    adjusted = (adjusted - brightness_min) / (brightness_max - brightness_min)
    return adjusted * opacity

def get_slice(data, view_type, index):
    if view_type == 'XY':
        slice_data = data[index, :, :]
    elif view_type == 'YZ':
        slice_data = np.rot90(data[:, :, index])
    else:  # XZ
        slice_data = np.rot90(data[:, index, :])
    return slice_data

def save_tiff_sequence(volume_data, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    for z in range(volume_data.shape[0]):
        output_path = os.path.join(output_dir, f'slice_{z:04d}.tif')
        tifffile.imwrite(output_path, volume_data[z], compression='zlib')

def apply_colormap(image, colormap):
    colored = colormap(image)
    return (colored * 255).astype(np.uint8)
