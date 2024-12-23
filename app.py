import streamlit as st
import tifffile
import numpy as np
import tempfile

class OptimizedTiffViewer:
    def __init__(self):
        self.data = None
        self.views = ['XZ', 'XY', 'YZ']
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
    
    def GetSlice(self, view_type, index, brightness_min, brightness_max):
        if view_type == 'XY':
            slice_data = self.data[index, :, :]
        elif view_type == 'YZ':
            slice_data = np.rot90(self.data[:, :, index])
        else:  # XZ
            slice_data = np.rot90(self.data[:, index, :])
        
        # Apply 90-degree rotations based on rotation state
        for _ in range(st.session_state.rotation_angle):
            slice_data = np.rot90(slice_data)
            
        return self.AdjustBrightness(slice_data, brightness_min, brightness_max)
    
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
                
                # Show buttons after file upload
                col1, col2 = st.sidebar.columns(2)
                with col1:
                    if st.button("Switch View"):
                        self.RotateView()
                with col2:
                    if st.button("Rotate 90°"):
                        self.Rotate90()
                
                # Brightness controls
                st.sidebar.subheader("Brightness Control")
                data_min = float(self.data.min())
                data_max = float(self.data.max())
                brightness_range = st.sidebar.slider(
                    "Brightness Range",
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
                
                # Display image with reduced size
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    st.image(
                        self.GetSlice(
                            current_view, 
                            slice_idx, 
                            brightness_range[0], 
                            brightness_range[1]
                        ),
                        use_column_width=True
                    )
                
            except Exception as e:
                st.error(f"Error processing TIFF stack: {str(e)}")

if __name__ == "__main__":
    viewer = OptimizedTiffViewer()
    viewer.Run()
