import numpy as np
from tifffile import imread, imwrite
import os
import matplotlib.pyplot as plt
from scipy.ndimage import uniform_filter

class DensityMapGenerator:
    def __init__(self, axon_mask_path, voxel_size=25, atlas_boundaries_path=None, kernel_size=5):
        """
        Initialize DensityMapGenerator with input data
        
        Parameters:
        -----------
        axon_mask_path : str
            Path to binary axon mask stack
        voxel_size : int
            Resolution in microns
        atlas_boundaries_path : str, optional
            Path to Allen Atlas boundaries stack
        kernel_size : int
            Size of kernel for density calculation
        """
        self.voxel_size = voxel_size
        self.kernel_size = kernel_size
        self.axon_mask = imread(axon_mask_path).astype(bool)
        self.atlas_boundaries = None
        if atlas_boundaries_path:
            self.atlas_boundaries = imread(atlas_boundaries_path)
            assert self.axon_mask.shape == self.atlas_boundaries.shape

    def calculate_density(self, stack):
        """
        Calculate density of white pixels using sliding window
        """
        # Use uniform filter to count pixels in neighborhood
        density = uniform_filter(stack.astype(float), 
                               size=self.kernel_size, 
                               mode='constant')
        return density

    def apply_thermal_colormap(self, stack):
        """
        Apply thermal colormap to density values
        """
        thermal_map = plt.cm.get_cmap('plasma')
        
        # Calculate density
        density = self.calculate_density(stack)
        
        # Normalize density values
        normalized = density/np.max(density)
        
        # Apply colormap
        colored = thermal_map(normalized)
        return (colored[:,:,:,:3] * 255).astype(np.uint8)

    def generate_density_stacks(self):
        """
        Generate density stacks for all three orientations
        """
        # Generate stacks for each viewing plane
        stack_xz = np.moveaxis(self.axon_mask, 1, 0)
        stack_yz = np.moveaxis(self.axon_mask, 0, 0)
        stack_xy = self.axon_mask
        
        # Calculate density and apply thermal colormap
        stack_xz = self.apply_thermal_colormap(stack_xz)
        stack_yz = self.apply_thermal_colormap(stack_yz)
        stack_xy = self.apply_thermal_colormap(stack_xy)
        
        # Add atlas boundaries if available
        if self.atlas_boundaries is not None:
            atlas_xz = np.moveaxis(self.atlas_boundaries, 1, 0)
            atlas_yz = np.moveaxis(self.atlas_boundaries, 0, 0)
            atlas_xy = self.atlas_boundaries
            
            # Add boundaries as black overlay
            stack_xz[atlas_xz > 0] = [255, 255, 255]
            stack_yz[atlas_yz > 0] = [255, 255, 255]
            stack_xy[atlas_xy > 0] = [255, 255, 255]
            
        return stack_xz, stack_yz, stack_xy

    def save_density_tiffstacks(self, output_dir='density_stacks'):
        """
        Save density stacks as RGB TIFF files
        """
        os.makedirs(output_dir, exist_ok=True)
        stack_xz, stack_yz, stack_xy = self.generate_density_stacks()
        
        # Define output paths
        output_paths = {
            'xz': os.path.join(output_dir, 'stack_xz.tif'),
            'yz': os.path.join(output_dir, 'stack_yz.tif'),
            'xy': os.path.join(output_dir, 'stack_xy.tif')
        }
        
        # Save stacks
        imwrite(output_paths['xz'], stack_xz, photometric='rgb')
        imwrite(output_paths['yz'], stack_yz, photometric='rgb')
        imwrite(output_paths['xy'], stack_xy, photometric='rgb')
        
        print(f"Stack dimensions:")
        print(f"XZ stack: {stack_xz.shape}")
        print(f"YZ stack: {stack_yz.shape}")
        print(f"XY stack: {stack_xy.shape}")
        print(f"\nTIFF stacks saved in: {os.path.abspath(output_dir)}")
        
        return list(output_paths.values())

def process_brain_data(axon_mask_path, atlas_path=None, output_dir='density_stacks', kernel_size=5):
    """
    Process brain data and generate density-based thermal colormap stacks
    """
    try:
        generator = DensityMapGenerator(
            axon_mask_path=axon_mask_path,
            atlas_boundaries_path=atlas_path,
            kernel_size=kernel_size
        )
        
        output_files = generator.save_density_tiffstacks(output_dir)
        
        print("\nGenerated files:")
        for file_path in output_files:
            print(f"- {file_path}")
            
    except Exception as e:
        print(f"Error processing brain data: {str(e)}")
        raise

if __name__ == "__main__":
    # Example usage
    axon_mask_path = r"F:\brainglobe\coumbia1\ch0\dMASK.tif"
    atlas_path = r"F:\brainglobe\coumbia1\ch0\boundaries.tiff"  # Optional
    
    process_brain_data(
        axon_mask_path=axon_mask_path,
        atlas_path=atlas_path,
        output_dir='density_stacks',
        kernel_size=5  # Adjust kernel size for density calculation
    )