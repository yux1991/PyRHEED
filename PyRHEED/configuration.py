#This program is used to generate configuration file for the PyRHEED program
#Last updated by Yu Xiang at 08/13/2018
#This code is written in Python 3.6.6 (32 bit)

import configparser
config = configparser.ConfigParser()
config['MenuDefault'] = {'image_path':'C:/RHEED/01192017 multilayer graphene on Ni/20 keV/Img0000.nef',\
                         'icon_path':'./icons/',\
                         'vertical_shift':0,\
                         'horizontal_shift':0}
config['InfoPanelDefault'] = {'sensitivity':361.13,\
                              'electron_energy':20,\
                              'azimuth':0,\
                              'scale_bar_length':5,\
                              'brightness':30,\
                              'black_level':50,\
                              'auto_wb':0,\
                              'integral_width':10,\
                              'chi_range':60,\
                              'PF_radius':200.,\
                              'PF_tilt':0.}

with open('./configuration.ini','w') as configfile:
    config.write(configfile)
