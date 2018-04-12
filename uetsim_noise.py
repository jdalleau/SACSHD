import numpy as np
import pandas as pd
import random
import math
from joblib import Parallel, delayed
import multiprocessing
from sklearn import preprocessing
import time
from sklearn import datasets
import uetlib
from scipy.stats import ttest_ind, ttest_rel
from sklearn.metrics.pairwise import euclidean_distances

def build_ensemble(data,n_estimators=50,nmin=None,coltypes=None):
	if nmin == None:
		nmin = math.floor(len(data)/3)
	similarities = []
	num_cores = multiprocessing.cpu_count()
	results = Parallel(n_jobs=num_cores)(delayed(uetlib.get_sim)(data,nmin,coltypes) for i in range(n_estimators))
	similarities = results
	return(np.sum(similarities,axis=0)/n_estimators)

def build_ensemble_inc(data,n_estimators=50,nmin=None,coltypes=None):
	if nmin == None:
		nmin = math.floor(len(data)/3)
	similarities = np.zeros((len(data),len(data)))
	num_cores = multiprocessing.cpu_count()
	results = Parallel(n_jobs=num_cores)(delayed(uetlib.get_sim_one)(data,nmin,coltypes) for i in range(n_estimators))
	similarities = results
	
	return(np.sum(similarities,axis=0)/n_estimators)

def compute_distance(similarity):
	out = [[0 for i in range(len(similarity))] for j in range(len(similarity))]
	for indexi,i in enumerate(similarity):
		for indexj,j in enumerate(similarity):
			out[indexi][indexj] = math.sqrt(1-similarity[indexi][indexj])
	return(np.array(out))

def compute_sim_intra_inter(similarity,classes):
	distinct_classes = np.unique(classes)
	indices = []
	for current in distinct_classes:
		indices.append(np.where(classes==current)[0])
	intrac_similarities = []
	interc_similarities = []
	for i in range(len(indices)):
		cluster1_indices = indices[i]
		for j in range(len(indices)):
			cluster2_indices = indices[j]
			if(i==j):
				local_sim = [similarity[i][j] for i in cluster1_indices for j in cluster2_indices if (i != j) ]
				intrac_similarities.extend(local_sim)
			else:
				local_sim = [similarity[i][j]  for i in cluster1_indices for j in cluster2_indices if (i != j)]
				interc_similarities.extend(local_sim)
	return((intrac_similarities, interc_similarities))

def test_differences(data,Y,coltype):
	global_difference = []
	for i in range(20):
		matrices = []
		for j in range(5):
			similarity = build_ensemble_inc(data, coltypes=coltype)
			matrices.append(similarity)
		similarity_matrix = np.sum(matrices, axis = 0)/5
		sims = compute_sim_intra_inter(similarity_matrix, Y)
		intrac = sims[0]
		interc = sims[1]
		intrac_mean = np.mean(intrac)
		interc_mean = np.mean(interc)
		global_difference.append(abs(interc_mean-intrac_mean))

	print("Summary of all the runs.\n")
	print("Mean difference between intercluster similarities and intracluster similarities : {0} (standard deviation : {1}) \n".format(np.mean(global_difference),np.std(global_difference)))
	print("----------\n")
	return((np.mean(global_difference),np.std(global_difference)))

def add_noise(data,percentage_data=1,percentage_noise=0.05):
    data_flat = data.flatten()
    indices = [i for i in range(len(data_flat))]
    indices = random.sample(indices,math.ceil(percentage_data*len(data_flat)))
    for index in indices:
        data_flat[index] = data_flat[index] + np.random.uniform(-percentage_noise*data_flat[index],percentage_noise*data_flat[index])
    return(np.reshape(data_flat,(data.shape[0],data.shape[1])))

out = []
for noise in [i for i in range(0,25)]:
	local_out = ()
	noise = 0.02*noise
	X, y = datasets.make_blobs(n_samples=500, centers=3, n_features=5,random_state=0)
	data = add_noise(X, percentage_noise=noise) 
	data_type = [0 for i in range(data.shape[1])]

	blob = (np.array(data), np.array(y),data_type)
	print("Synthetic dataset, 500 samples, 5 features. Noise = {0}".format(noise))
	diff = test_differences(*blob)

	local_out = diff + (noise,)
	out.append(local_out)
	del blob

print(out)
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
x_ax = [value[2] for value in out]

noise_mean = [value[0] for value in out]
noise_std = [value[1] for value in out]
plt.ylim(0,1)

plt.errorbar(x_ax,noise_mean,yerr = noise_std)

plt.xlabel("Noise strength")
plt.ylabel("Mean difference between intracluster and intercluster similarities")
plt.savefig("noise_strength_blobs.png")
plt.clf()
plt.cla()
plt.close()

out = []

for noise in [i for i in range(0,25)]:
	local_out = ()
	noise = noise * 0.02
	X, y = datasets.make_moons(n_samples=500,noise = noise, random_state=0)
	data = X
	data_type = [0 for i in range(data.shape[1])]

	blob = (np.array(data), np.array(y),data_type)
	print("Synthetic dataset, 500 samples. Noise = {0}".format(noise))
	diff = test_differences(*blob)

	local_out = diff + (noise,)
	out.append(local_out)
	del blob

print(out)
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
x_ax = [value[2] for value in out]

noise_mean = [value[0] for value in out]
noise_std = [value[1] for value in out]
plt.ylim(0,1)

plt.errorbar(x_ax,noise_mean,yerr = noise_std)

plt.xlabel("Noise strength (standard deviation of gaussian noise)")
plt.ylabel("Mean difference between intracluster and intercluster similarities")
plt.savefig("noise_strength_moons.png")
plt.clf()
plt.cla()
plt.close()


out = []
for noise in range(0,25):
	local_out = ()
	noise = 0.02*noise
	data_iris = datasets.load_iris()
	data = add_noise(data_iris.data, percentage_noise=noise)
	iris_type = [0 for i in range(data.shape[1])]
	iris = (np.array(data), np.array(data_iris.target),iris_type)
	print("Iris dataset - With noise. Noise = {0}".format(noise))
	diff = test_differences(*iris)

	local_out = diff + (noise,)
	out.append(local_out)
	del iris

print(out)
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
x_ax = [value[2] for value in out]

noise_mean = [value[0] for value in out]
noise_std = [value[1] for value in out]
plt.ylim(0,1)

plt.errorbar(x_ax,noise_mean,yerr = noise_std)

plt.xlabel("Noise strength")
plt.ylabel("Mean difference between intracluster and intercluster similarities")
plt.savefig("noise_strength_iris.png")
plt.clf()
plt.cla()
plt.close()