import time
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.colors as mcolors
from scipy.interpolate import LinearNDInterpolator
from scipy.interpolate import NearestNDInterpolator
from scipy.interpolate import CloughTocher2DInterpolator
import pandas
from collections import Counter
from scipy.stats import chisquare
from scipy.stats import power_divergence
from sklearn.mixture import BayesianGaussianMixture

class Sample():
    def __init__(self,nx,ny):
        df = pandas.read_csv(filepath_or_buffer="c:/users/yux20/documents/05042018 MoS2/3D_Map_04162019.txt",sep=" ",names=["x","y","z","intensity"],na_values="NaN")#,nrows=10)
        df["intensity"] = np.power(df["intensity"],6)
        z_list = np.unique(df["z"].to_numpy())
        for z in z_list:
            mask = df["z"]==z
            df["x"].loc[mask], df["y"].loc[mask], df["intensity"].loc[mask] = df["x"].loc[mask]*np.cos(df["y"].loc[mask]/180*np.pi),\
                 df["x"].loc[mask]*np.sin(df["y"].loc[mask]/180*np.pi), df["intensity"].loc[mask]/df["intensity"].loc[mask].sum()
        df_new = pandas.DataFrame({})
        for z in z_list:
            start_time = time.time()
            x_range = np.linspace(-7,7,nx)
            y_range = np.linspace(-7,7,ny)
            x,y=np.meshgrid(x_range,y_range)
            mask = df["z"]==z
            points = list(zip(df["x"].loc[mask].to_list(),df["y"].loc[mask].to_list()))
            interp = CloughTocher2DInterpolator(points,df["intensity"].loc[mask],fill_value=0)
            print("z = {}: finished generating interpolator, using {:.2f}s".format(z,time.time()-start_time))
            start_time = time.time()
            interp_2d = np.abs(interp(x,y))
            print("z = {}: finished interpolation, using {:.2f}s".format(z,time.time()-start_time))
            start_time = time.time()
            intensity_sum = np.sum(np.concatenate(interp_2d))
            print("z = {}: finished sum, using {:.2f}s".format(z,time.time()-start_time))
            start_time = time.time()
            shp = np.product(x.shape)
            data = pandas.DataFrame({"x":np.reshape(x,shp), "y":np.reshape(y,shp), "z":np.full(shp,z), "intensity":np.reshape(interp_2d/intensity_sum,shp)})
            df_new = df_new.append(data,ignore_index=True)
        df_new.to_csv("c:/users/yux20/documents/05042018 MoS2/interpolated_2D_stack_large.csv")

if __name__ == "__main__":
    test = Sample(1000,1000)
