#!/usr/bin/env python

# IMPORTS
import state
import sys
import utils
import uuid
from subprocess import PIPE, run, Popen
from threading import Thread, Lock
import random
import query
from CONSTANTS import *
from os.path import join

# Given a newModel and its corresponding label (= labels[userLabelIdx]),
# this function generates the positive example for the examples file
# of that label, as well as the negative examples for all other examples
# files, and appends them there.
def updateExampleFiles(newModel, labels, userLabelIdx):
	labelExamplesPaths = state.get('labelExamplesPaths')
	userLabel = labels[userLabelIdx]

	for idx in range(len(labels)):
		currLabel = labels[idx]
		if idx == userLabelIdx:
			newEx = utils.generatePosExample(newModel)
		else:
			newEx = utils.generateNegExample(newModel)

		file = open(labelExamplesPaths[currLabel], 'a')
		file.write('\n' + newEx + '\n')
		file.close()

# This function gets a random model from the clusters, taking
# cluster weights into account. It also assumes that there exists
# at least one model in the clusters (i.e. it can always find a model)
def getNewModel():
	clusters       = state.get('clusters')
	clusterWeights = state.get('clusterWeights')
	clusterKeys    = list(clusters.keys())
	
	weightedClustersList = list()

	for ck in clusterKeys:
		weightedClustersList += [ck] * clusterWeights[ck]

	randCluster = random.choice(weightedClustersList)

	newModel = utils.getModelFromList(clusters[randCluster])
	# print('Model id: ' + newModel.modelId)
	# input()
	if clusters[randCluster] == []:
		del clusters[randCluster]

	return newModel

# This function asks the user whether they wish to classify a model
# at random or if they wish to bias the model they get with a set of
# constraints, called a 'query'; it returns True if they choose the former,
# and False if they choose the latter.
def askModelType():
	print('(1) Generate random model for classification?')
	print('(2) Generate model based on a custom set of constraints?')
	ansMap = {
		1: RANDOM_STRING,
		2: QUERY_STRING
	}

	ansCnt = 2

	if utils.noLabelsExist():
		ansCnt += 1
		ansMap[ansCnt] = NO_LABEL_STRING
		print('(' + str(ansCnt) + ') Generate model with no predicted label?')

	if utils.multipleLabelsExist():
		ansCnt += 1
		ansMap[ansCnt] = MULTIPLE_LABELS_STRING
		print('(' + str(ansCnt) + ') Generate model with multiple predicted labels?')

	while True:
		try:
			ans = int(input('Your answer: '))
			if (ans < 1 or ans > ansCnt):
				raise ValueError
			return ansMap[ans]
		except ValueError:
			print('Invalid label index, please try again!')
			continue

# This function generates a new model, randomly or based on a user
# query (knows this by asking the user), computes the label(s) for
# that model, given the current hypotheses, then generates the model
# diagram, along with the predicted label(s). It gets the label from
# the user (unless they choose to "Skip", in which case start function
# over), it updates the examples files, and also updates the hypotheses
# that need to be recomputed (those that incorrectly labelled the current
# model). No need to return anything, this process is self-contained.
def newClassif():
	# utils.printModelLists()
	# input()
	labels   = state.get('labels')
	mustLabelModels = state.get('mustLabelModels')
	modelType = askModelType()
	isFromClusters = modelType == RANDOM_STRING

	if (modelType == RANDOM_STRING):
		newModel = getNewModel()
	elif (modelType == QUERY_STRING):
		newModel = query.getModelWithQuery()
		if not newModel:
			print()
			newClassif()
			return
	elif (modelType == NO_LABEL_STRING):
		newModel, isFromClusters = utils.getNoLabelModel()
	else:
		# modelType == MULTIPLE_LABELS_STRING
		newModel, isFromClusters = utils.getMultipleLabelsModel()

	utils.checkNoEmptyClusters()

	# print('isFromClusters: ' + str(isFromClusters))
	# input()

	labelsForModel = utils.computeLabelsForModelObj(newModel, forceCompute=(not isFromClusters))
	utils.generateModelDiagram(newModel, labelsForModel)

	# print(newModel.modelId)
	print('\n* Please classify the model on the screen. Choose (index) from the following:')
	for l in range(len(labels)):
		print('(' + str(l + 1) + ') ' + labels[l])

	print('\n(0) Skip\n')

	while True:
		try:
			ans = int(input('Your answer: '))
			if (ans < 0 or ans > len(labels)):
				raise ValueError
			break
		except ValueError:
			print('Invalid label index, please try again!')
			continue

	# If ans was 0, user wants to skip current model, so redo newClassif
	# to get a new model
	if (ans == 0):
		if isFromClusters:
			state.get('skippedModels').append(newModel)
		print()
		newClassif()
		return

	state.get('labelledModelIds').append(newModel.modelId)
	userLabelIdx       = ans - 1
	userLabel          = labels[userLabelIdx]

	utils.removeModelFromLists(newModel.modelId)

	if utils.isModelFromSample(newModel.modelId):
		state.get('userLabelCounters')[userLabel] += 1

	hypothesesToUpdate = state.get('hypothesesToUpdate')
	if (not len(labelsForModel)):
		hypothesesToUpdate.add(userLabel)
	elif (len(labelsForModel) == 1 and labelsForModel[0] != userLabel):
		hypothesesToUpdate.add(userLabel)
		hypothesesToUpdate.add(labelsForModel[0])
	else:
		isCovered = False
		for mLabel in labelsForModel:
			if (mLabel != userLabel):
				hypothesesToUpdate.add(mLabel)
			else:
				isCovered = True
		if (not isCovered):
			hypothesesToUpdate.add(userLabel)
	updateExampleFiles(newModel, labels, userLabelIdx)

# This function is to be run in threads by runILASPCommands; it computes the ILASP
# program for the label "label", then runs that program and places the output in
# the mapping "outputs". This is done in a thread-safe manner using lock
def runILASPCMDInThread(backGroundStr, genericBiasStr, label, outputs, lock):
	ILASPFileStr  = backGroundStr

	examplesStr   = utils.getExamplesString(label)
	ILASPFileStr += examplesStr

	biasStr       = genericBiasStr.replace('$$LABEL$$', ILASP_LABEL_STRING)
	ILASPFileStr += biasStr

	programPath = utils.createILASPProgram(label, ILASPFileStr)
	ILASPCmd = list(GENERIC_ILASP_CMD)
	ILASPCmd.append(programPath)

	out, err = Popen(ILASPCmd, stdout=PIPE, universal_newlines=True).communicate()
	if err:
		raise RuntimeError('Error encountered while generating hypotheses.')

	lock.acquire()
	outputs[label] = out
	lock.release()

# Note that labelsToUpdateHypotheses is a actually a list of all the labels whose
# hypotheses need to be updated. Upon termination, it updates the hypotheses in the
# state and clears the list of hypotheses to be updated.
def runILASPCommands(labelsToUpdateHypotheses):
	backGroundStr = utils.getBackgroundString()
	biasConstantsStr = utils.computeBiasConstants()
	genericBiasStr = utils.getBiasString().replace('$$CONSTANTS$$', biasConstantsStr)
	outputs = {}
	lock = Lock()
	threads = list()

	for label in labelsToUpdateHypotheses:
		threads.append(Thread(target=runILASPCMDInThread, 
							args=(backGroundStr, genericBiasStr, label, outputs, lock),
							daemon=True))

	for thread in threads:
		thread.start()

	for thread in threads:
		thread.join()

	utils.updateHypotheses(outputs)
	state.get('hypothesesToUpdate').clear()

# This represents the main interaction classification cycle
def computeHypotheses():
	# By default, ask to classify a model to have something to work with
	newClassif()

	# This simulates a do-until loop; it asks the user to classify models until
	# they decide to stop, at which point the hypotheses are computed based on the
	# classified examples, and then outputted for the user to analyze.
	# At that point, the user can decide to go back to manual classification to
	# obtain better hypotheses (basically start the function over) or exit the loop
	# and use the hypotheses they have now in order to automatically classify all 
	# the initial provided models
	while True:
		# Check if no further models available, compute hypotheses and return if true
		if (utils.clustersAreEmpty(state.get('clusters'))):
			utils.printTitle('No other models to classify available, computing hypotheses.')
			hypothesesToUpdate = list(state.get('hypothesesToUpdate'))

			if (len(hypothesesToUpdate)):
				utils.printTitle('Please wait while the hypotheses are being computed, this might take a while.')
				runILASPCommands(hypothesesToUpdate)
				utils.printHypotheses()
			else:
				utils.printTitle('All new labels agree with the last hypotheses computed.')
			return

		continueClassif = input('\nWould you like to classify another model? (y/n) ').lower()
		if (continueClassif == 'y'):
			print()
			newClassif()
		elif (continueClassif == 'n'):
			hypothesesToUpdate = list(state.get('hypothesesToUpdate'))
			if (len(hypothesesToUpdate)):
				utils.printTitle('Please wait while the hypotheses are being computed, this might take a while.')
				runILASPCommands(hypothesesToUpdate)
				utils.printHypotheses()
				state.set('labelPredictionsUpdated', False)
			else:
				utils.printTitle('All new labels agree with the last hypotheses computed.')

			utils.checkAndRecluster()
			utils.resetMustLabelModels()

			print('Would you like to:')
			print('(1) Continue classification to improve current class hypotheses?')
			print('(2) Use current hypotheses to automatically classify all initial data?')
			while True:
				try:
					ans = int(input('Your answer (1/2): '))
					if (ans < 1 or ans > 2):
						raise ValueError
					break
				except ValueError:
					continue

			if (ans == 1):
				print()
				computeHypotheses()
			return
