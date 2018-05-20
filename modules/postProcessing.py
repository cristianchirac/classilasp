import utils
import state
from constants import *

import uuid
from threading import Thread, Lock
from os.path import join

# This is the function to be run by each of the CLASSIFICATION_THREADS threads
# It terminates only when a thread is unable to pop a model string from the list 
# anymore (because it's empty), otherwise it computes the label(s) for that model
# and appends them to the file storing all models' labels, then tries to pop again
def popModelsAndClassify(modelsStrings, labelsFile, labelsCounter, lockR, lockW):
	tempDirPath      = state.get('tempDirPath')
	tempFilePath     = join(tempDirPath, uuid.uuid4().hex + '.las')
	output           = state.get('classifOutput')
	totalNumOfModels = state.get('numOfInputModels')
	maxModelsAtOnce  = MODELS_PER_CLASSIF_PROC

	while True:
		currModels = list()
		lockR.acquire()
		if (not len(modelsStrings)):
			lockR.release()
			return

		numOfModels = min(maxModelsAtOnce, len(modelsStrings))
		# print(numOfModels)
		for idx in range(numOfModels):
			currModels.append(modelsStrings.pop())
		# print(len(modelsStrings))
		lockR.release()

		modelObjs = list(map(utils.computeModelObjFromModelStr, currModels))
		labelPredsForModels = utils.computeLabelPredsForModels(modelObjs, tempFilePath)
		modelLabelsMap = utils.getModelLabelsMap(labelPredsForModels)

		lockW.acquire()

		output = state.get('classifOutput')
		for label in labelPredsForModels:
			output += label + '.\n'
		state.set('classifOutput', output)

		for model in list(modelLabelsMap.keys()):
			if len(modelLabelsMap[model]) == 1:
				labelsCounter[modelLabelsMap[model][0]] += 1
			else:
				labelsCounter[MULTIPLE_LABELS_STRING] += 1

		labelsCounter[NO_LABEL_STRING] += numOfModels - len(list(modelLabelsMap.keys()))

		utils.printProgressBar(totalNumOfModels, numOfIterations=numOfModels)
		lockW.release()

# This is the function that classifies all the initial models based on the last
# computed hypotheses; because each model can be classified independently, we can
# do this concurrently, using a number of CLASSIFICATION_THREADS many threads
# Each thread will work with one model string at a time, compute its label and
# output it to a file in the same directory as the initial file
# As a result, models (with their labels) will be outputted in a random order,
# almost certainly different than the one in the input file
# Note that we ensure thread safe accesses when popping a new model string from the
# given list using lockR and writing to the file using lockW  
def classifyAllModels(modelsAbsPath):
	modelsStrings = utils.getModelsStrings(modelsAbsPath)
	utils.initProgressBar()

	numOfThreads = CLASSIFICATION_THREADS
	lockR = Lock()
	lockW = Lock()

	classFilePath = utils.computeClassFilePath()
	labelsFile = open(classFilePath, 'a')
	labelsCounter = utils.getBlankLabelsCounter()

	threads = list()
	for tIdx in range(numOfThreads):
		threads.append(Thread(target=popModelsAndClassify, 
							args=(modelsStrings, labelsFile, labelsCounter, lockR, lockW),
							daemon=True))
	
	utils.printTitle('All initial models are about to be labelled, this might take a while.')
	
	for thread in threads:
		thread.start()

	for thread in threads:
		thread.join()

	labelsFile.write(state.get('classifOutput'))
	state.set('classifOutput', '')

	print('* All models have been succesfully labelled and saved in:\n' + classFilePath + '\n')
	labelsFile.close()

	labelKeys = list(labelsCounter.keys())
	nonZeroLabels = [l for l in labelKeys if labelsCounter[l] > 0]

	labels = list(map(lambda l: l + ': ' + str(labelsCounter[l]), nonZeroLabels))
	values = list(map(lambda l: labelsCounter[l], nonZeroLabels))
	utils.generatePieChart(labels, values, title='Labels distribution')
	