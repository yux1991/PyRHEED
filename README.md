# PyRHEED

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

It is written and tested with Python 3.6.6. The GUI is created using PyQt5. The *simulate_RHEED* module utilized the [pymatgen](http://pymatgen.org/) library to read CIF files and create structures. Major features include:

1. RHEED raw image process using [rawpy](https://pypi.org/project/rawpy/) and intensity profile extraction which is accelerated by [numpy](https://www.numpy.org/) vecterization. Construction of 2D reciprocal space map and pole figure is automated. The 3D data could be saved as *.vtp format, which could be processed by [paraview](https://www.paraview.org).
2. Batch fit RHEED line profiles with pre-defined peak functions (only Gaussian is supported right now) and save the formatted results.
3. Visualize the fit results and generate a report.
4. Simulate the statistical factor from a Markov process, assuming a certain distribution of step density on a hexagonal surface. More details are disscussed in the paper by [Spadacini et al.](https://www.sciencedirect.com/science/article/pii/0039602883904922).
5. Read the crystal structure from a CIF file and create a customized structure by stacking different crystalline materials together. Calculate the diffraction pattern from this structure based on the kinematic diffraction theory.

## Requirements
- pyqt5
- numpy
- matplotlib
- rawpy
- pandas
- scipy
- pymatgen
- lxml
- pillow

## Usage
1. Installation
    ```
    git https://github.com/yux1991/PyRHEED.git
    cd source
    python main.py
    ```
2. Load data

    The RHEED data are often images. Both raw image and compressed image files could be directly opened 
    through the open file dialog. The image is automatically converted to a gray scale image. Note that
    JPEG only supports up to 8-bit RGB data. Please use other image formats if a higher dynamic range is desiered.
    
3. Analysis

    Depending on the purpose, several kinds of data analysis can be done with this application. The RHEED pattern
    simulation, structure factor simulation are modules that does not depend on the experimental data.
    
## Modules 
- broadening: batch automatic fit of the RHEED line profiles
- browser: browse files inside the working directory
- canvas: display images, draw shapes and take user input
- configuration: change default configurations
- cursor: display cursor-related information
- generate_report: generate a report that visualize the fitting results
- graph_3D_surface: visualize the 3D surface in reciprocal space
- main: the main module
- manual_fit: manually fit the RHEED line profile to initialize the fitting parameters
- my_widgets: customized widgets
- plot_chart: a customized widget based on QChart, for visualization of the fitting results
- preference: modify default settings
- process: the backend processes
- profile_chart: a customized widget based on QChart, for visualization of the line scan profiles
- properties: control the dynamic parameters of the program
- reciprocal_space_mapping: construct the 2D/3D reciprocal space map and the pole figure
- simulate_RHEED: simulate the diffraction pattern from a given atomic structure 
- statistical_factor: calculate the statistical factor assuming a Markov process 
- test: the test module
- window: the main window of the application

## Contact
Please contact Yu Xiang at [yux1991@gmail.com](mailto:yux1991@gmail.com) if you have any questions or suggestions.
