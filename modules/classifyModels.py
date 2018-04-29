#!/usr/bin/env python

# IMPORTS
import state
import sys
import utils
import uuid
from subprocess import PIPE, run, Popen
from threading import Thread, Lock
import random
from constants import GENERIC_ILASP_CMD
from os.path import join

def updateExampleFiles(newModel, labels, userLabelIdx):
	labelExamplesPaths = state.get('labelExamplesPaths')
	userLabel = labels[userLabelIdx]

	for idx in range(len(labels)):
		currLabel = labels[idx]
		if idx == userLabelIdx:
			newEx = utils.generatePosExample(newModel, currLabel)
		else:
			newEx = utils.generateNegExample(newModel, currLabel)

		file = open(labelExamplesPaths[currLabel], 'a')
		file.write('\n' + newEx + '\n')
		file.close()

def getNewModel():
	clusters       = state.get('clusters')
	clusterWeights = state.get('clusterWeights')
	clusterKeys    = list(clusters.keys())
	
	weightedClustersList = list()

	for ck in clusterKeys:
		weightedClustersList += [ck] * clusterWeights[ck]

	randCluster = random.choice(weightedClustersList)

	newModel = clusters[randCluster].pop()
	# print('Model id: ' + newModel.modelId)
	if clusters[randCluster] == []:
		del clusters[randCluster]

	return newModel

def newClassif():
	labels   = state.get('labels')

	newModel = getNewModel()
	labelsForModel = utils.computeLabelsForModelObj(newModel)
	utils.generateModelDiagram(newModel, labelsForModel)

	print('Please classify the model on the screen. Choose (index) from the following:\n')
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
		state.get('skippedModels').append(newModel)
		print()
		newClassif()
		return

	userLabelIdx       = ans - 1
	userLabel          = labels[userLabelIdx]
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

def runILASPCMDInThread(backGroundStr, genericBiasStr, label, outputs, lock):
	ILASPFileStr  = backGroundStr

	examplesStr   = utils.getExamplesString(label)
	ILASPFileStr += examplesStr

	biasStr       = genericBiasStr.replace('$$LABEL$$', label)
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
# hypotheses need to be updated
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
