import streamlit as st
import os
from datetime import datetime

st.title("Create Experiment")

# Create experiments directory
experiments_dir = os.path.join(os.path.dirname(__file__), '../experiments')
os.makedirs(experiments_dir, exist_ok=True)

# Experiment name input
experiment_name = st.text_input("Enter experiment name")

if experiment_name:
    experiment_dir = os.path.join(experiments_dir, experiment_name)
    os.makedirs(experiment_dir, exist_ok=True)
    st.success(f"Created experiment: {experiment_name}")
    st.session_state['current_experiment'] = experiment_dir
else:
    st.info("Please enter an experiment name to continue")
