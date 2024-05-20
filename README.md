# <img src="https://github.com/yux1991/PyRHEED/blob/master/src/icons/icon.png" width="48"/> PyRHEED
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://GitHub.com/yux1991/PyRHEED/graphs/commit-activity) [![GitHub license](https://img.shields.io/github/license/yux1991/PyRHEED.svg)](https://github.com/yux1991/PyRHEED/blob/master/LICENSE) [![Ask Me Anything !](https://img.shields.io/badge/Ask%20me-anything-1abc9c.svg)](mailto:yux1991@gmail.com)

## Table of Content
1. [Description](README.md#Description)
2. [Requirements](README.md#Requirements)
3. [Usage](README.md#Usage)
4. [Modules](README.md#Structure)
5. [Contact](README.md#Contact)

## Description
This project is used for reflection high energy electron diffraction (RHEED) data analysis and theoretical simulation. 
RHEED is an electron diffraction technique using a relatively high energy (5~30 keV) beam of electrons with a grazing incident
angle. It is very surface sensitive, with a penetration depth of only a few nanometers. Since the scattering factor of electrons
is about four orders magnetude higher than that of X-ray, RHEED is especially suitable to characterize 2D materials such as graphene
which can hardly be detected using XRD. Another merit of RHEED is that the spot size is very large (~1 cm), which enables it to
measure the wafer-scale average of the material's properties including the lattice constants, grain orientation distribution and
even defect density.

It is written and tested with Python 3.7.4 (64 bit). The GUI is created using PyQt6. The *simulate_RHEED* module utilized the [pymatgen](http://pymatgen.org/) library to read CIF files and create structures. Major features include:

1. RHEED raw image process using [rawpy](https://pypi.org/project/rawpy/) and intensity profile extraction which is accelerated by [numpy](https://www.numpy.org/) vecterization. Construction of 2D reciprocal space map and pole figure is automated. The 3D data could be saved as *.vtp format, which could be processed by [paraview](https://www.paraview.org).
2. Batch fit RHEED line profiles with pre-defined peak functions (including Gaussian function and Voigt function) and save the formatted results.
3. Visualize the fit results and generate a report.
4. Simulate the statistical factor from a Markov process, assuming a certain distribution of step density on a hexagonal surface. More details are disscussed in the paper by [Spadacini et al.](https://www.sciencedirect.com/science/article/pii/0039602883904922).
5. Read the crystal structure from a CIF file and create a customized structure by stacking different crystalline materials together. Calculate the diffraction pattern from this structure based on the kinematic diffraction theory.
6. Simulate the reciprocal 3D structure from a given structure. The atomic model can be created within this program. It is especially designed to simulate the diffraction from a 2D translational antiphase domain model, see details in the paper by [Lu et al.](https://www.sciencedirect.com/science/article/pii/0039602881905410).

## Usage
1. Prerequisite

    It's recommended that you have the Python 3.12.2 (64 bit) installed and added to the system PATH.

2. Installation
    ```
    git clone https://github.com/yux1991/PyRHEED.git
    cd PyRHEED
    python -m venv env_pyrheed
    source ./env_pyrheed/bin/activate
    pip install -r requirements.txt 
    ```
3. Usage
    ```
    cd src
    python main.py
    ```
4. Load data

    The RHEED data are often images. Both raw image and compressed image files could be directly opened through the open file dialog. The image is automatically converted to a gray scale image. Note that JPEG only supports up to 8-bit RGB data. Please use other image formats if a higher dynamic range is desiered.
    
5. Analysis

    Depending on the purpose, several kinds of data analysis can be done with this application. The RHEED pattern simulation, structure factor simulation are modules that does not depend on the experimental data.

6. Run Scenario

    Load the predefined scenario or create a customized one, then run the scenario to automatically generate the results
    
## Modules 
- broadening: batch automatic fit of the RHEED line profiles
- browser: browse files inside the working directory
- canvas: display images, draw shapes and take user input
- configuration: change default configurations
- cursor: display cursor-related information
- generate_report: generate a report that visualize the fitting results
- graph_3D_surface: visualize the 3D surface in reciprocal space
- kikuchi: simulate the Kikuchi pattern from a non-reconstructed crystal surface
- main: the main module
- manual_fit: manually fit the RHEED line profile to initialize the fitting parameters
- my_widgets: customized widgets
- plot_chart: a customized widget based on QChart, for visualization of the fitting results
- preference: modify default settings
- process: the backend processes
- process_monitor: monitor the consumption of memory (not complete)
- profile_chart: a customized widget based on QChart, for visualization of the line scan profiles
- properties: control the dynamic parameters of the program
- reciprocal_space_mapping: construct the 2D/3D reciprocal space map and the pole figure
- scenario: select or customize a scenario, then run the scenario
- simulate_RHEED: simulate the diffraction pattern from a given atomic structure. This module is also capable of generating structures containing translational antiphase domain (APD) model and calculating the corresponding diffraction pattern. 
- statistical_factor: calculate the statistical factor assuming a Markov process 
- test: the test module
- translational_antiphase_domain: calculate the 1D and 2D profile from a translational APD model
- window: the main window of the application
- write_scenario: write the default scenario

## Demonstrations
1. Extract line profiles:

![line](https://user-images.githubusercontent.com/38077812/111377405-9a688e00-866e-11eb-8ef2-b25386f10d27.gif)


2. Extract features on a sphere:

![tilt](https://user-images.githubusercontent.com/38077812/111377452-aa806d80-866e-11eb-91eb-8a7f103c2077.gif)


3. Construct azimuthal RHEED:

![Azimuth](https://user-images.githubusercontent.com/38077812/111377562-cbe15980-866e-11eb-8c64-5fa6137a0d96.gif)


4. Vertical scan:

![Vertical](https://user-images.githubusercontent.com/38077812/111377572-ce43b380-866e-11eb-8b8f-e6ccd2e74a68.gif)


5. 3D surface view:

![surface](https://user-images.githubusercontent.com/38077812/111377787-1236b880-866f-11eb-8e52-60f3235085df.gif)


6. Regression analysis:

![fit](https://user-images.githubusercontent.com/38077812/111377799-16fb6c80-866f-11eb-96cd-f01dff3425ab.gif)


7. Interactive data visualization:

![report](https://user-images.githubusercontent.com/38077812/111377803-18c53000-866f-11eb-94ff-4ea16daaef3e.gif)


8. Kikuchi line simulation:

![kikuchi](https://user-images.githubusercontent.com/38077812/111377813-1bc02080-866f-11eb-8043-28bc199f8cd5.gif)


9. Domain boundary statistics:

![simulation](https://user-images.githubusercontent.com/38077812/111377823-1f53a780-866f-11eb-8b26-4638de0200c0.gif)


## Contact
Please contact Yu Xiang at [yux1991@gmail.com](mailto:yux1991@gmail.com) if you have any questions or suggestions.
