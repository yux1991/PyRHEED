#This program is used to analyze and simulate the RHEED pattern
#Last updated by Yu Xiang at 08/12/2018
#This code is written in Python 3.6.6 (32 bit)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Standard Libraries ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import numpy as np
import tkinter as tk
from tkinter import *
from TkMain import *
from TkInfoPanel import *
import configparser

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ main function ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def main():
    root = Tk()
    root.title('PyRHEED')
    root.state('zoomed')
    config = configparser.ConfigParser()
    config.read('./configuration.ini')
    MainDefault = dict(config['MainDefault'].items())
    InfoPanelDefault = dict(config['InfoPanelDefault'].items())
    main_window = TkMain(root,MainDefault)
    info_panel = TkInfoPanel(main_window,InfoPanelDefault)
    root.mainloop()

if __name__ == '__main__':
    main()
