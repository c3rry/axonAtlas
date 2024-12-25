# axonAtlas
developing a a Streamlit web application, that can convert light-sheet imaged mouse brains into axon segmentation masks, density based heatmaps, and Allen Atlas region axon based 3D visualizations. This web application implements BrainReg and TrailMap to integrate an automatic Allen Atlas Volumetric Registration aided by a computer vision model to detect optimal data orientation, as well as a 3D CNN for axonal extraction
# setup
open anaconda prompt and enter this command to clone the axonAtlas github repo:
##
    git clone https://github.com/c3rry/axonAtlas.git
##
    cd axonAtlas
##
clone the trailMap github repo:
##
    git clone https://github.com/albert597/TRAILMAP.git
##
create the anaconda enviorment with the base TrailMap dependencies with this command: 
##
    conda create -n axonAtlas tensorflow-gpu=2.1 opencv=3.4.2 pillow=7.0.0
##
then enter the conda enviorment with this command:
##
    conda activate axonAtlas
##
then download all app dependencies with this command:
##
    pip install streamlit tifffile matplotlib brainreg
##
run the streamlit app with this command:
##
    streamlit run app.py --server.maxUploadSize 1000
##


