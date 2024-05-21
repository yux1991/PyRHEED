import math
from fractions import Fraction
import matplotlib.pyplot as plt
import numpy as np
import os

class function(object):
    def __init__(self):
        super(function,self).__init__()

    def prob_1d(self,lc_a,lc_b,p):
        ratio = Fraction(lc_a/lc_b).limit_denominator()
        B, A = ratio.numerator, ratio.denominator
        #print("A="+str(A)+", B="+str(B))
        result = [[],[]]
        for k in range(1,A):
            d = lc_b*(1+k*B/A-math.floor(k*B/A))
            norm_p = (1-p)**(k-1)*p/(1-(1-p)**(A-1))
            result[0].append(np.around(d,5))
            result[1].append(np.around(norm_p,5))
        return result

    def prob_2d(self,lc_a1, lc_b1,lc_a2, lc_b2, theta, p):
        ratio = Fraction(lc_a1/lc_b1).limit_denominator()
        B1, A1 = ratio.numerator, ratio.denominator
        ratio = Fraction(lc_a2/lc_b2).limit_denominator()
        B2, A2 = ratio.numerator, ratio.denominator
        result = [[],[]]
        for k1 in range(1,A1):
            for k2 in range(1,A2):
                d1 = lc_b1*(1+k1*B1/A1-math.floor(k1*B1/A1))
                d2 = lc_b2*(1+k2*B2/A2-math.floor(k2*B2/A2))
                norm_p = (1-p)**(k1-1)*p/(1-(1-p)**(A1-1))*(1-p)**(k2-1)*p/(1-(1-p)**(A2-1))
                result[0].append(np.around(np.sqrt(d1**2+d2**2+2*d1*d2*np.cos(theta/180*np.pi)),5))
                result[1].append(np.around(norm_p,5))
        return result
    
    def plot_prob_1d(self,lc_a, lc_b,prob_list):
        figure = plt.figure()
        fontsize = 20
        fontname='arial'
        ax = figure.add_subplot(111)
        for p in prob_list:
            distribution = self.prob_1d(lc_a, lc_b,p)
            d_exp = sum(x*y for x,y in zip(distribution[0],distribution[1]))
            ax.scatter(distribution[0],distribution[1],label="p="+str(p)+", E(d)="+str(np.around(d_exp,3)))
        ax.legend()
        #ax.text(min(distribution[0]),max(distribution[1])*0.95,"a="+str(lc_a)+", b="+str(lc_b),fontsize=fontsize,fontweight='heavy')
        ax.set_xlabel('d (Angstrom)',fontsize=fontsize, fontname=fontname)
        ax.set_ylabel('Probability',fontsize=fontsize, fontname=fontname)
        ax.set_xticklabels(np.around(ax.get_xticks(),4),fontsize=fontsize, fontname=fontname)
        ax.set_yticklabels(np.around(ax.get_yticks(),4),fontsize=fontsize, fontname=fontname)
        plt.tight_layout()
        plt.show()

    def plot_prob_2d(self,lc_a1, lc_b1,lc_a2, lc_b2, theta, prob_list):
        figure = plt.figure()
        fontsize = 20
        fontname='arial'
        ax = figure.add_subplot(111)
        for p in prob_list:
            distribution = self.prob_2d(lc_a1, lc_b1,lc_a2, lc_b2, theta,p)
            d_exp = sum(x*y for x,y in zip(distribution[0],distribution[1]))
            ax.scatter(distribution[0],distribution[1],label="p="+str(p)+", E(d)="+str(np.around(d_exp,3)))
        ax.legend()
        ax.set_xlabel('d (Angstrom)',fontsize=fontsize, fontname=fontname)
        ax.set_ylabel('Probability',fontsize=fontsize, fontname=fontname)
        ax.set_xticklabels(np.around(ax.get_xticks(),4),fontsize=fontsize, fontname=fontname)
        ax.set_yticklabels(np.around(ax.get_yticks(),4),fontsize=fontsize, fontname=fontname)
        plt.tight_layout()
        plt.show()

    def plot_prob_2d_sim(self,input_list):
        lc_a, lc_b = 4.76,3.15
        figure = plt.figure()
        fontsize = 20
        fontname='arial'
        ax = figure.add_subplot(111)
        for filename in input_list:
            file = open(filename,"r")
            distribution = [[float(line.strip('\n').split('\t')[0]),int(line.strip('\n').split('\t')[1])] for line in list(file)]
            distance = [pair[0]*lc_b for pair in distribution]
            count = [pair[1] for pair in distribution]
            total_count = sum(count)
            probability = [np.around(c/total_count,5) for c in count]
            d_exp = sum(x*y for x,y in zip(distance, probability))
            label = os.path.split(os.path.splitdrive(filename)[1])[1].split('.')[0]
            print(d_exp,label)
            ax.scatter(distance, probability,label=label)
        ax.legend()
        #ax.text(min(distance),max(probability)*0.95,"a="+str(lc_a)+", b="+str(lc_b),fontsize=fontsize,fontweight='heavy')
        ax.set_xlabel('d (Angstrom)',fontsize=fontsize, fontname=fontname)
        ax.set_ylabel('Probability',fontsize=fontsize, fontname=fontname)
        ax.set_xticklabels(np.around(ax.get_xticks(),4),fontsize=fontsize, fontname=fontname)
        ax.set_yticklabels(np.around(ax.get_yticks(),4),fontsize=fontsize, fontname=fontname)
        plt.tight_layout()
        plt.show()

    def plot_prob_1d_and_2d(self,lc_a,lc_b,prob_list,input_path):
        for p in prob_list:
            figure = plt.figure()
            fontsize = 20
            fontname='arial'
            ax = figure.add_subplot(111)
            distribution = self.prob(lc_a, lc_b,p)
            d_exp = sum(x*y for x,y in zip(distribution[0],distribution[1]))
            ax.scatter(distribution[0],distribution[1],label="1D: p="+str(p)+", E(d)="+str(np.around(d_exp,3)))
            filename=input_path+str(p)+"-70.0nm/"+str(p)+'.txt'
            file = open(filename,"r")
            distribution = [[float(line.strip('\n').split('\t')[0]),int(line.strip('\n').split('\t')[1])] for line in list(file)]
            distance = [pair[0]*lc_b for pair in distribution]
            count = [pair[1] for pair in distribution]
            total_count = sum(count)
            probability = [np.around(c/total_count,5) for c in count]
            d_exp = sum(x*y for x,y in zip(distance, probability))
            label = "2D: p="+str(p)+", E(d)="+str(np.around(d_exp,3))
            ax.scatter(distance, probability,label=label)
            ax.legend()
            #ax.text(min(distance),max(probability)*0.95,"a="+str(lc_a)+", b="+str(lc_b),fontsize=fontsize,fontweight='heavy')
            ax.set_xlabel('d (Angstrom)',fontsize=fontsize, fontname=fontname)
            ax.set_ylabel('Probability',fontsize=fontsize, fontname=fontname)
            ax.set_xticklabels(np.around(ax.get_xticks(),4),fontsize=fontsize, fontname=fontname)
            ax.set_yticklabels(np.around(ax.get_yticks(),4),fontsize=fontsize, fontname=fontname)
            plt.tight_layout()
        plt.show()


if __name__ == "__main__":
    lc_a, lc_b = 4.76,3.15
    prob_list = [0.001,0.002,0.004,0.008,0.016,0.032,0.064,0.128]
    input_list = ["C:/Dev/PyRHEED/source/RHEED scenario 02212021/0.001-70.0nm/0.001.txt","C:/Dev/PyRHEED/source/RHEED scenario 02212021/0.002-70.0nm/0.002.txt",\
                "C:/Dev/PyRHEED/source/RHEED scenario 02212021/0.004-70.0nm/0.004.txt","C:/Dev/PyRHEED/source/RHEED scenario 02212021/0.008-70.0nm/0.008.txt",\
                "C:/Dev/PyRHEED/source/RHEED scenario 02212021/0.016-70.0nm/0.016.txt","C:/Dev/PyRHEED/source/RHEED scenario 02212021/0.032-70.0nm/0.032.txt",\
                "C:/Dev/PyRHEED/source/RHEED scenario 02212021/0.064-70.0nm/0.064.txt","C:/Dev/PyRHEED/source/RHEED scenario 02212021/0.128-70.0nm/0.128.txt",]
    input_path = "C:/Dev/PyRHEED/source/RHEED scenario 02212021/"
    worker = function()
    #worker.plot_prob_1d(lc_a,lc_b,prob_list)
    worker.plot_prob_2d(lc_a,lc_b,lc_a,lc_b,120,prob_list)
    #worker.plot_prob_2d_sim(input_list)
    #worker.plot_prob_1d_and_2d(lc_a,lc_b,prob_list,input_path)