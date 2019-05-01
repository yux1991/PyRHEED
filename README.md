# PyRHEED

# Table of Content
1. [Description](README.md#Description)
2. [Requirements](README.md#Requirements)
3. [Usage](README.md#Usage)
4. [Modules](README.md#Structure)
5. [Contact](README.md#Contact)

# Description
This application is used for RHEED analysis and simulation. It is written with Python 3.6.6. Major features include:
## RHEED raw image process and intensity profile extraction. Construction of 2D reciprocal space map and pole figure is automated. The 3D data could be saved as *.vtp format, which could be processed by [Paraview](https://www.paraview.org). A screenshot of the example is shown below:
![alt text](https://raw.githubusercontent.com/yux1991/PyRHEED/master/sreenshots/Screenshot_main.JPG)
## Batch fit RHEED line profiles with pre-defined peak functions (only Gaussian is supported right now) and save the formatted results. A screenshot of the example is shown below:
![alt text](https://raw.githubusercontent.com/yux1991/PyRHEED/master/screenshots/Screenshot_broadening.JPG)
## Visualize the fit results and generate a report. A screenshot of the example is shown below:
![alt text](https://raw.githubusercontent.com/yux1991/PyRHEED/master/screenshots/Screenshot_generate_report.JPG)
## Simulate the statistical factor from a Markov process, assuming a certain distribution of step density on a hexagonal surface. More details are disscussed in the paper by [Spadacini et al.](https://www.sciencedirect.com/science/article/pii/0039602883904922). A screenshot of the example is shown below:
![alt text](https://raw.githubusercontent.com/yux1991/PyRHEED/master/screenshots/Screenshot_Simulate_Statistical_Factor.JPG)
## Read the crystal structure from a CIF file and create a customized structure by stacking different crystalline materials together. Calculate the diffraction pattern from this structure using the kinematic diffraction theory.
![alt text](https://raw.githubusercontent.com/yux1991/PyRHEED/master/screenshots/Screenshot_Simulate_RHEED.JPG)

# Requirements
- PyQt5
- Numpy
- Matplotlib
- Rawpy
- Pandas
- Scipy
- pymatgen
- lxml

# Usage
    git https://github.com/yux1991/PyRHEED.git
    python Main.py

# Modules 
- Browser: browse files inside the working directory
- Canvas: display images, draw shapes and take user input
- Configuration: change default configurations
- Cursor: display cursor-related information
- Graph3DSurface: visualize the 3D surface in reciprocal space
- Main: the main module
- Menu: define menubar and the menu actions
- Process: processes raw image
- ProfileChart: display line scan profiles
- Properties: control the dynamic parameters of the program
- SimulateRHEED: simulate the diffraction pattern from a given atomic structure 
- StatisticalFactor: calculate the statistical factor assuming a Markov process 
- Test: the test module
- Window: the main window of the application

# Contact
Please contact Yu Xiang (yux1991@gmail.com) if you have any questions or suggestions.
