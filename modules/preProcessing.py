#!/usr/bin/env python

import state
import utils
import random
from functools import reduce
import numpy as np
from sklearn.cluster import MeanShift
from architectureClasses import Port, Edge, PortGroup, Component, Model
from constants import MAX_RELEVANT_MODELS

# This function takes a list of model strings, as provided in the input file,
# and returns the afferent Model objects, with custom names or not, depending
# on the value of the bool nameComponents
def computeAllModelObjects(models, nameComponents):
	allModels = list()

	for modelStr in models:
		newModelObj = utils.computeModelObjFromModelStr(modelStr, nameComponents)
		allModels.append(newModelObj)

	return allModels

# This function uses the MeanShift function imported from sklearn.cluster
# in order to compute cluster "centers", which are points in the Nth dimension,
# where N is the total number of component types, such that, informally, they
# "surround" themselves with as many given points as possible, and then clusters
# those points together in one cluster for that center point
# It returns ms.labels_, which is a list as long as the list of models, and has
# in its ith position the cluster number of the ith model
def clusterModels(compositionVectors):
	ms = MeanShift()
	ms.fit(compositionVectors)
	labels = ms.labels_
	# cluster_centers = ms.cluster_centers_
	# print(labels)
	# input()
	return labels

# Given a list of models and all the componentNames used in the input file,
# this function computes for each model the "composition vector", which has
# in the Nth position the number of the Nth component type that model uses,
# and returns a list containing all these vectors in the same order as the 
# models list in the input
def computeModelsCompositionVectors(models, compNames):
	compositionVectors = list()
	for model in models:
		compositionVector = [0] * len(compNames)
		for comp in model.getUsedComponents():
			compType = comp.name
			compositionVector[compNames.index(compType)] += 1
		compositionVectors.append(compositionVector)
	return compositionVectors

# This function takes a list - labels - of the same size as the list of models
# such that each element in labels is the clusterId of the model at that
# same position with respect to the list of models
# E.g. ([_, _, M, _], [_, _, 2, _]) says that model M is in cluster 2
def computeClusterToModelMapping(models, labels):
	numOfClusters = len(np.unique(labels))
	mapping = {}

	for clusterIdx in range(numOfClusters):
		mapping[clusterIdx] = list()

	for idx in range(len(models)):
		mapping[labels[idx]].append(models[idx])

	return mapping

# This function parses the input file in order to get the strings for all models
# Since the number of such models can potentially be very large, we only select
# (randomly) MAX_RELEVANT_MODELS out of them to work with, if their number exceeds
# this constant value; otherwise, we work with all models
# The function then returns the map from clusterIds to the actual clusters of models
def parseInputFile(nameComponents):
	modelStrings = utils.getModelsStrings(state.get('inputFilePath'))
	state.set('numOfInputModels', len(modelStrings))

	# Note that we want to randomize order of models, regardless of whether
	# we select a subsample of MAX_RELEVANT_MODELS or we keep all samples
	# This helps after clustering is done, because we won't have to generate
	# a random index within each cluster, since the models in that cluster will
	# already be in random order after this step, so we can just pop the first/last one
	randomSampleSize = min(len(modelStrings), MAX_RELEVANT_MODELS)
	modelStrings = random.sample(modelStrings, randomSampleSize)

	models = computeAllModelObjects(modelStrings, nameComponents)
	compNames = list(map(lambda comp: comp.name, state.get('componentTypes')))

	compositionVectors = computeModelsCompositionVectors(models, compNames)
	labels = clusterModels(compositionVectors)

	return computeClusterToModelMapping(models, labels)
