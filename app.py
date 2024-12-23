import streamlit as st
import tifffile
import numpy as np
import tempfile
import matplotlib.cm as cm

class OptimizedTiffViewer:
    def __init__(self):
        self.data = None
        self.views = ['XZ', 'XY', 'YZ']
        self.colormaps = {
            'bone': cm.bone,
            'binary': cm.binary,
            'spring': cm.spring,
            'summer': cm.summer,
            'autumn': cm.autumn,
            'winter': cm.winter,
            'pink': cm.pink,
            'viridis': cm.viridis,
            'plasma': cm.plasma,
            'inferno': cm.inferno,
            'magma': cm.magma,
            'hot': cm.hot,
            'cool': cm.cool,
            'coolwarm': cm.coolwarm,
            'RdYlBu': cm.RdYlBu,
            'seismic': cm.seismic,
            'turbo': cm.turbo,
            'hsv': cm.hsv
        }
        if 'current_view' not in st.session_state:
            st.session_state.current_view = 0
        if 'rotation_angle' not in st.session_state:
            st.session_state.rotation_angle = 0
    
    def SetupPage(self):
        st.set_page_config(page_title="TIFF Stack Viewer", layout="wide")
        st.title("axonAtlas")
    
    @staticmethod
    @st.cache_data
    def LoadTiff(uploadedFile):
        with tempfile.NamedTemporaryFile(delete=False, suffix='.tif') as tmpFile:
            tmpFile.write(uploadedFile.getvalue())
            with tifffile.TiffFile(tmpFile.name) as tif:
                return tif.asarray()
    
    def AdjustBrightness(self, image, brightness_min, brightness_max):
        adjusted = np.clip(image, brightness_min, brightness_max)
        adjusted = (adjusted - brightness_min) / (brightness_max - brightness_min)
        return adjusted
    
    def GetSlice(self, view_type, index, brightness_min, brightness_max, colormap):
        # Get the slice data
        if view_type == 'XY':
            slice_data = self.data[index, :, :]
        elif view_type == 'YZ':
            slice_data = np.rot90(self.data[:, :, index])
        else:  # XZ
            slice_data = np.rot90(self.data[:, index, :])
        
        # Apply rotations
        for _ in range(st.session_state.rotation_angle):
            slice_data = np.rot90(slice_data)
        
        # Apply brightness adjustment
        adjusted = self.AdjustBrightness(slice_data, brightness_min, brightness_max)
        
        # Apply colormap
        colored = self.colormaps[colormap](adjusted)
        
        # Convert to uint8 for display
        return (colored * 255).astype(np.uint8)
    
    def RotateView(self):
        st.session_state.current_view = (st.session_state.current_view + 1) % 3
    
    def Rotate90(self):
        st.session_state.rotation_angle = (st.session_state.rotation_angle + 1) % 4
    
    def Run(self):
        self.SetupPage()
        uploadedFile = st.sidebar.file_uploader("Upload TIFF stack", type=['tif', 'tiff'])
        
        if uploadedFile is not None:
            try:
                self.data = self.LoadTiff(uploadedFile)
                z_max, y_max, x_max = self.data.shape
                
                # Controls in sidebar
                st.sidebar.subheader("Controls")
                
                # Colormap selection
                selected_colormap = st.sidebar.selectbox(
                    "Select Colormap",
                    list(self.colormaps.keys()),
                    index=0
                )
                
                # View rotation buttons
                col1, col2 = st.sidebar.columns(2)
                with col1:
                    if st.button("Switch View"):
                        self.RotateView()
                with col2:
                    if st.button("Rotate 90°"):
                        self.Rotate90()
                
                # Brightness controls
                st.sidebar.subheader("Brightness")
                data_min = float(self.data.min())
                data_max = float(self.data.max())
                brightness_range = st.sidebar.slider(
                    "Range",
                    min_value=data_min,
                    max_value=data_max,
                    value=(data_min, data_max)
                )
                
                # Current view display
                current_view = self.views[st.session_state.current_view]
                st.subheader(f"Current View: {current_view}")
                
                # Set slice range based on view
                if current_view == 'XY':
                    max_slice = z_max - 1
                    slice_label = "Z"
                elif current_view == 'YZ':
                    max_slice = x_max - 1
                    slice_label = "X"
                else:  # XZ
                    max_slice = y_max - 1
                    slice_label = "Y"
                
                slice_idx = st.slider(slice_label, 0, max_slice, max_slice//2)
                
                # Display image
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    st.image(
                        self.GetSlice(
                            current_view, 
                            slice_idx, 
                            brightness_range[0], 
                            brightness_range[1],
                            selected_colormap
                        ),
                        use_column_width=True
                    )
                
            except Exception as e:
                st.error(f"Error processing TIFF stack: {str(e)}")

if __name__ == "__main__":
    viewer = OptimizedTiffViewer()
    viewer.Run()
