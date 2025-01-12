import streamlit as st
import os
from lib.utils import load_tiff, save_tiff_sequence

st.title("Axon Segmentation")

if 'current_experiment' not in st.session_state:
    st.warning("Please create an experiment first")
else:
    uploaded_files = st.file_uploader(
        "Upload TIFF stacks",
        type=['tif', 'tiff'],
        accept_multiple_files=True
    )
    
    if uploaded_files:
        for uploaded_file in uploaded_files:
            if st.button(f"Prepare {uploaded_file.name} for TrailMap"):
                output_dir = os.path.join(
                    st.session_state['current_experiment'],
                    f'trailmap_input_{uploaded_file.name.replace(".tif", "")}'
                )
                data = load_tiff(uploaded_file)
                save_tiff_sequence(data, output_dir)
                st.success(f"Saved frames to: {output_dir}")
        
        if st.button("Process All TrailMap Inputs"):
            try:
                import sys
                import subprocess
                
                input_folders = [d for d in os.listdir(st.session_state['current_experiment']) 
                               if os.path.isdir(os.path.join(st.session_state['current_experiment'], d)) 
                               and d.startswith('trailmap_input')]
                
                if input_folders:
                    cmd = [sys.executable, "TRAILMAP/segment_brain_batch.py"] + \
                          [os.path.join(st.session_state['current_experiment'], d) for d in input_folders]
                    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                            text=True, bufsize=1, universal_newlines=True)
                    
                    output = st.empty()
                    while True:
                        line = process.stdout.readline()
                        if not line and process.poll() is not None:
                            break
                        output.text(line)
                    
                    if process.poll() == 0:
                        st.success("TrailMap processing completed!")
                    else:
                        st.error("TrailMap processing failed!")
                else:
                    st.warning("No TrailMap input folders found")
            except Exception as e:
                st.error(f"Failed to run TrailMap: {str(e)}")
