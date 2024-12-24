import streamlit as st
import numpy as np
import os
import matplotlib.cm as cm
from utils import load_tiff, adjust_brightness, get_slice, save_tiff_sequence, apply_colormap

# Set page config at top level
st.set_page_config(page_title="axonAtlas", layout="wide")

class OptimizedTiffViewer:
    def __init__(self):
        self.volumes = {}
        self.views = ['XZ', 'XY', 'YZ']
        self.colormaps = {
            'viridis': cm.viridis,
            'plasma': cm.plasma,
            'hot': cm.hot,
            'cool': cm.cool,
            'gray': cm.gray
        }
        if 'current_view' not in st.session_state:
            st.session_state.current_view = 0
        if 'rotation_angle' not in st.session_state:
            st.session_state.rotation_angle = 0
    
    def SetupPage(self):
        st.title("axonAtlas")
    
    def GetOverlaidSlice(self, view_type, index):
        combined_slice = None
        for vol_id, vol_data in self.volumes.items():
            slice_data = get_slice(vol_data['data'], view_type, index)
            
            for _ in range(st.session_state.rotation_angle):
                slice_data = np.rot90(slice_data)
            
            adjusted = adjust_brightness(
                slice_data,
                vol_data['brightness_range'][0],
                vol_data['brightness_range'][1],
                vol_data['opacity']
            )
            colored = apply_colormap(adjusted, self.colormaps[vol_data['colormap']])
            
            if combined_slice is None:
                combined_slice = colored
            else:
                combined_slice = np.maximum(combined_slice, colored)
        
        return combined_slice if combined_slice is not None else np.zeros((1,1))
    
    def Run(self):
        self.SetupPage()
        
        # Create output area for terminal logs
        terminal_output = st.empty()
        
        uploaded_files = st.sidebar.file_uploader(
            "Upload TIFF stacks",
            type=['tif', 'tiff'],
            accept_multiple_files=True
        )
        
        if uploaded_files:
            for uploaded_file in uploaded_files:
                vol_id = uploaded_file.name
                if vol_id not in self.volumes:
                    self.volumes[vol_id] = {
                        'data': load_tiff(uploaded_file),
                        'opacity': 1.0,
                        'colormap': list(self.colormaps.keys())[0]
                    }
            
            max_z = max(vol['data'].shape[0] for vol in self.volumes.values())
            max_y = max(vol['data'].shape[1] for vol in self.volumes.values())
            max_x = max(vol['data'].shape[2] for vol in self.volumes.values())
            
            st.sidebar.subheader("View Controls")
            col1, col2 = st.sidebar.columns(2)
            with col1:
                if st.button("Switch View"):
                    st.session_state.current_view = (st.session_state.current_view + 1) % 3
            with col2:
                if st.button("Rotate 90°"):
                    st.session_state.rotation_angle = (st.session_state.rotation_angle + 1) % 4
            
            st.sidebar.subheader("Volume Controls")
            for vol_id in self.volumes:
                with st.sidebar.expander(f"Controls for {vol_id}"):
                    vol_data = self.volumes[vol_id]
                    
                    vol_data['colormap'] = st.selectbox(
                        "Colormap",
                        list(self.colormaps.keys()),
                        key=f"colormap_{vol_id}"
                    )
                    
                    data_min = float(vol_data['data'].min())
                    data_max = float(vol_data['data'].max())
                    vol_data['brightness_range'] = st.slider(
                        "Brightness",
                        min_value=data_min,
                        max_value=data_max,
                        value=(data_min, data_max),
                        key=f"brightness_{vol_id}"
                    )
                    
                    vol_data['opacity'] = st.slider(
                        "Opacity",
                        min_value=0.0,
                        max_value=1.0,
                        value=1.0,
                        key=f"opacity_{vol_id}"
                    )
                    
                    if st.button("Prepare for TrailMap", key=f"trailmap_{vol_id}"):
                        output_dir = os.path.join(
                            os.path.dirname(__file__),
                            f'trailmap_input_{vol_id.replace(".tif", "")}'
                        )
                        save_tiff_sequence(vol_data['data'], output_dir)
                        st.success(f"Saved frames to: {output_dir}")
            
            # TrailMap batch processing button
            st.sidebar.subheader("TrailMap Processing")
            if st.sidebar.button("Process All TrailMap Inputs"):
                try:
                    import sys
                    import subprocess
                    
                    input_folders = [d for d in os.listdir(os.path.dirname(__file__)) 
                                   if os.path.isdir(d) and d.startswith('trailmap_input')]
                    
                    if input_folders:
                        cmd = [sys.executable, "TRAILMAP/segment_brain_batch.py"] + input_folders
                        process = subprocess.Popen(
                            cmd,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT,
                            text=True,
                            bufsize=1,
                            universal_newlines=True
                        )
                        
                        output_text = ""
                        while True:
                            output = process.stdout.readline()
                            if output == '' and process.poll() is not None:
                                break
                            if output:
                                output_text += output
                                terminal_output.text(output_text)
                        
                        if process.poll() == 0:
                            st.sidebar.success("TrailMap processing completed!")
                        else:
                            st.sidebar.error("TrailMap processing failed!")
                    else:
                        st.sidebar.warning("No TrailMap input folders found")
                        
                except Exception as e:
                    st.sidebar.error(f"Failed to run TrailMap: {str(e)}")
            
            current_view = self.views[st.session_state.current_view]
            st.subheader(f"Current View: {current_view}")
            
            if current_view == 'XY':
                slice_idx = st.slider("Z", 0, max_z-1, max_z//2)
            elif current_view == 'YZ':
                slice_idx = st.slider("X", 0, max_x-1, max_x//2)
            else:  # XZ
                slice_idx = st.slider("Y", 0, max_y-1, max_y//2)
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.image(
                    self.GetOverlaidSlice(current_view, slice_idx),
                    use_column_width=True
                )

if __name__ == "__main__":
    viewer = OptimizedTiffViewer()
    viewer.Run()
