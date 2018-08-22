#This program is used to analyze and simulate the RHEED pattern
#Last updated by Yu Xiang at 08/12/2018
#This code is written in Python 3.6.6 (32 bit)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Standard Libraries ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import numpy as np
import tkinter as tk
from tkinter import *
from tkinter import ttk
import TkMenu
import TkCanvas
import TkInfoPanel
import configparser

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ main function ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def main():
    root = Tk()
    root.title('PyRHEED')
    root.state('zoomed')
    config = configparser.ConfigParser()
    config.read('./configuration.ini')
    MenuDefault = dict(config['MenuDefault'].items())
    InfoPanelDefault = dict(config['InfoPanelDefault'].items())
    root.rowconfigure(1,weight=1)
    root.columnconfigure(0,weight=1)
    pan = ttk.PanedWindow(root,orient=HORIZONTAL)
    pan.grid(row=1,column=0,sticky=N+S+E+W)
    menu = TkMenu.menu(root,MenuDefault)
    canvas = TkCanvas.canvas(pan,MenuDefault)
    info_panel = TkInfoPanel.info_panel(root,pan,InfoPanelDefault)
    root.title('PyRHEED: ~/'+menu.get_default_file_name())
    root.mainloop()

if __name__ == '__main__':
    main()
