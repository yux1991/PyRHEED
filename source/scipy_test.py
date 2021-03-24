import time
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.colors as mcolors
from scipy.interpolate import LinearNDInterpolator
from scipy.interpolate import NearestNDInterpolator
import pandas
from collections import Counter
from scipy.stats import chisquare
from scipy.stats import power_divergence
from sklearn.mixture import BayesianGaussianMixture

class Test():

    def __init__(self):
        # Parameters of the dataset
        self.random_state, self.n_components = 2, 4
        self.fit_colors = list(mcolors.XKCD_COLORS.values())

        self.covars = np.array([[[.1, .0], [.0, .1]],
                                [[.1, .0], [.0, .1]],
                                [[.1, .0], [.0, .1]],
                                [[.1, .0], [.0, .1]]])
        self.samples = np.array([2000, 5000, 7000, 2000])
        self.means = np.array([[-1.0, -.70],
                               [.0, .0],
                               [.5, .30],
                               [1.0, .70]])

    def chi_square(self,c,n):
        s = np.ceil(np.random.rand(n)*c)
        ct = list(Counter(s).values())
        print(chisquare(ct))
        print(power_divergence(ct,lambda_=1))

    def gmm(self):
        # mean_precision_prior= 0.8 to minimize the influence of the prior
        estimators = [
            ("Infinite mixture with a Dirichlet process\n prior and" r"$\gamma_0=$",
            BayesianGaussianMixture(
                weight_concentration_prior_type="dirichlet_process",
                n_components=3 * self.n_components, reg_covar=0, init_params='random',
                max_iter=1500, mean_precision_prior=.8,
                random_state=self.random_state, verbose=0), [1, 1000, 100000])]

        # Generate data
        rng = np.random.RandomState(self.random_state)
        X = np.vstack([
            rng.multivariate_normal(self.means[j], self.covars[j], self.samples[j])
            for j in range(self.n_components)])
        y = np.concatenate([np.full(self.samples[j], j, dtype=int)
                            for j in range(self.n_components)])

        # Plot results in two different figures
        for (title, estimator, concentrations_prior) in estimators:
            plt.figure(figsize=(4.7 * 3, 8))
            plt.subplots_adjust(bottom=.04, top=0.90, hspace=.05, wspace=.05,
                                left=.03, right=.99)

            gs = gridspec.GridSpec(3, len(concentrations_prior))
            for k, concentration in enumerate(concentrations_prior):
                estimator.weight_concentration_prior = concentration
                estimator.fit(X)
                self.plot_results(plt.subplot(gs[0:2, k]), plt.subplot(gs[2, k]), estimator,
                            X, y, r"%s$%.1e$" % (title, concentration),
                            plot_title=k == 0)

        plt.show()

    def samp(self):
        start_time = time.time()
        raw_3d = pandas.read_csv(filepath_or_buffer="c:/users/yux20/documents/05042018 MoS2/3D_Map_04162019.txt",sep=" ",names=["x","y","z","intensity"],na_values="NaN")
        length = raw_3d.index[-1]+1
        x_min,x_max = raw_3d["x"].min(), raw_3d["x"].max()
        y_min,y_max = raw_3d["y"].min(), raw_3d["y"].max()
        z_min,z_max = raw_3d["z"].min(), raw_3d["z"].max()

        nx,ny = 500,500
        nz = int((z_max-z_min)/(x_max-x_min)*nx)

        x_range = np.linspace(int(x_min/np.sqrt(2)),int(x_max/np.sqrt(2)),nx)
        y_range = np.linspace(int(x_min/np.sqrt(2)),int(x_max/np.sqrt(2)),ny)
        z_range = np.linspace(z_min,z_max,nz)

        x,y,z=np.meshgrid(x_range,y_range,z_range)
        subset=[]
        i = 0
        while i < length:
            radius = abs(raw_3d.iat[i,0])
            intensity = raw_3d.iat[i,3]
            step = int(x_max/radius*10) if radius>x_max*0.2 else 50
            subset.append(i)
            i +=step
        print("length of the resampled data is {}".format(len(subset)))

        print("finished meshgrid, using {:.2f}s".format(time.time()-start_time))
        start_time = time.time()

        rawx = raw_3d.iloc[subset,[0]].T.to_numpy()*np.cos(raw_3d.iloc[subset,[1]].T.to_numpy()/np.pi)
        rawy = raw_3d.iloc[subset,[0]].T.to_numpy()*np.sin(raw_3d.iloc[subset,[1]].T.to_numpy()/np.pi)
        rawz = raw_3d.iloc[subset,[2]].T.to_numpy()
        intensity = np.power(raw_3d.iloc[subset,[3]].T.to_numpy()[0],4)
        print("finished converting, using {:.2f}s".format(time.time()-start_time))
        start_time = time.time()

        interp = LinearNDInterpolator(list(zip(rawx[0],rawy[0],rawz[0])),intensity,fill_value=0)
        print("finished generating interpolator, using {:.2f}s".format(time.time()-start_time))
        start_time = time.time()
        interp_3d = interp(x,y,z)
        print("finished interpolation, using {:.2f}s".format(time.time()-start_time))
        start_time = time.time()
        intensity_sum = np.sum(np.concatenate(interp_3d))
        print("finished sum, using {:.2f}s".format(time.time()-start_time))
        start_time = time.time()
        output = open("c:/users/yux20/documents/05042018 MoS2/interpolated_3D_map.txt",mode='w')
        for i in range(nx):
            for j in range(ny):
                for k in range(nz):
                    row = "\t".join([str(np.around(x[j][i][k],4)),str(np.around(y[j][i][k],4)),str(np.around(z[j][i][k],4)),str(np.around(interp_3d[j][i][k]/intensity_sum,10))])+"\n"
                    output.write(row)
        output.close()
        print("finished writting, using {:.2f}s".format(time.time()-start_time))

    def plot_ellipses(self,ax, weights, means, covars):
        for n in range(means.shape[0]):
            eig_vals, eig_vecs = np.linalg.eigh(covars[n])
            unit_eig_vec = eig_vecs[0] / np.linalg.norm(eig_vecs[0])
            angle = np.arctan2(unit_eig_vec[1], unit_eig_vec[0])
            # Ellipse needs degrees
            angle = 180 * angle / np.pi
            # eigenvector normalization
            eig_vals = 2 * np.sqrt(2) * np.sqrt(eig_vals)
            ell = mpl.patches.Ellipse(means[n], eig_vals[0], eig_vals[1],
                                    180 + angle, edgecolor='black')
            ell.set_clip_box(ax.bbox)
            ell.set_alpha(weights[n])
            ell.set_facecolor(self.fit_colors[n])
            ax.add_artist(ell)

    def plot_results(self,ax1, ax2, estimator, X, y, title, plot_title=False):
        ax1.set_title(title)
        ax1.scatter(X[:, 0], X[:, 1], s=5, marker='o', color='lightgray', alpha=0.8)
        ax1.set_xlim(-2., 2.)
        ax1.set_ylim(-3., 3.)
        ax1.set_xticks(())
        ax1.set_yticks(())
        self.plot_ellipses(ax1, estimator.weights_, estimator.means_,
                    estimator.covariances_)

        ax2.get_xaxis().set_tick_params(direction='out')
        ax2.yaxis.grid(True, alpha=0.7)
        for n in range(estimator.means_.shape[0]):
            k,w = n, estimator.weights_[n]
            ax2.bar(k, w, width=0.9, color=self.fit_colors[k], zorder=3,
                    align='center', edgecolor='black')
            ax2.text(k, w + 0.007, "%.1f%%" % (w * 100.),
                    horizontalalignment='center')
        ax2.set_xlim(-.6, 2 * self.n_components - .4)
        ax2.set_ylim(0., 1.1)
        ax2.tick_params(axis='y', which='both', left=False,
                        right=False, labelleft=False)
        ax2.tick_params(axis='x', which='both', top=False)

        if plot_title:
            ax1.set_ylabel('Estimated Mixtures')
            ax2.set_ylabel('Weight of each component')

if __name__ == "__main__":
    test = Test()
    #test.chi_square(c=100,n=100000)
    #test.gmm()
    test.samp()
