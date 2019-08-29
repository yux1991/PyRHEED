import configparser

config = configparser.ConfigParser()
config['TAPD'] = {'epi_cif_path':'C:/Google Drive/Documents/CIF/MoS2_3.15.cif',
                  'sub_cif_path':'C:/Google Drive/Documents/CIF/Sapphire_4.76.cif', 
                  'destination':'C:/Google Drive/Documents/RHEED/RHEED simulation results/MoS2 TAPD 08262019/',
                  'x_max':50,
                  'y_max':50,
                  'z_min':0,
                  'z_max':0.5,
                  'x_shift':0,
                  'y_shift':0,
                  'z_shift':0,
                  'number_of_K_para_steps':500,
                  'number_of_K_perp_steps':1,
                  'Kx_range_min':-3,
                  'Kx_range_max':3,
                  'Ky_range_min':-3,
                  'Ky_range_max':3,
                  'Kz_range_min':0,
                  'Kz_range_max':10,
                  'camera_horizontal_rotation':0,
                  'camera_vertical_rotation':90,
                  'camera_zoom_level':190,
                  'plot_font_size':30,
                  'add_atoms':'True',
                  'add_substrate':'False',
                  'add_epilayer':'True',
                  'plot_log_scale':'True',
                  'save_size_distribution':'True',
                  'save_boundary_statistics':'True',
                  'save_boundary':'False',
                  'save_voronoi_diagram':'False',
                  'save_scene':'True',
                  'save_2D_map_image':'True',
                  'save_2D_map_data':'True',
                  'lattice_or_atoms':'lattice',
                  'colormap':'jet',
                  'distribution':'completely random',
                  'density':0.1
                  }

with open('./default_scenario.ini','w') as configfile:
    config.write(configfile)
