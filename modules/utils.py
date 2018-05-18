#!/usr/bin/env python

from os.path import abspath, relpath, dirname, basename, exists, join, realpath
from subprocess import PIPE, run, Popen
from threading import Thread, Lock
from graphviz import Graph
import uuid
import shutil
import sys
import os

import matplotlib
matplotlib.use("agg")
import matplotlib.pyplot as plt

import state
from constants import *
from architectureClasses import Port, Edge, PortGroup, Component, Model

def printSepLine(size):
	print(' ' + ('-' * size))

# This surrounds title strings with line chars to make them more visually noticeable
def printTitle(s):
	print()
	printSepLine(len(s) + 2)
	print('| ' + s + ' |')
	printSepLine(len(s) + 2)
	print()

def initProgressBar():
	state.set('iterationNum', 0)

def printProgressBar(total, numOfIterations=1):
	iteration = state.get('iterationNum') + numOfIterations
	state.set('iterationNum', iteration)

	relProgress = iteration / float(total)
	percent = ("{0:.2f}").format(100 * relProgress)
	length = 50
	filledLength = int(length * relProgress)
	bar = '█' * filledLength + '-' * (length - filledLength)
	print('\r%s |%s| %s%%' % ('Progress:', bar, percent), end = '\r')

	if (iteration == total):
		print('\n')

def askYesOrNo():
	while True:
		ans = input('Your answer (y/n): ').lower()
		if (ans == 'y' or ans == 'n'):
			return ans

def setParamsFromArgs(args):
	for arg in args:
		if arg == '-p':
			state.set('prenamedComponents', True)


# This function recursively checks that two lists have the exact same elements,
# potentially in different orders; if they are of the same non-zero length, then
# remove from both lists all elements equal to one of the lists first element
# and call the function on the remaining lists; otherwise, those are trivial
# base cases
# Note that this is O(N^2), but the lists are assumed to be relatively small in
# size, therefore sorting them to get a better complexity algorithm is not necessary
def checkListsHaveSameElements(l1, l2):
	if len(l1) != len(l2): return False
	if len(l1) == 0: return True

	elem = l1[0]
	l1WithoutElem = list(filter(lambda e: e != elem, l1))
	l2WithoutElem = list(filter(lambda e: e != elem, l2))

	return checkListsHaveSameElements(l1WithoutElem, l2WithoutElem)

def getArgsFromPred(pred):
	i1 = pred.find('(')
	i2 = pred.find(')')
	return pred[i1 + 1 : i2].split(',')

def getModelId(modelPred):
	return getArgsFromPred(modelPred)[0]

def getNodeIdFromNodePred(nodePred):
	return getArgsFromPred(nodePred)[1]

def getNodeTypeFromNodePred(nodePred):
	return getArgsFromPred(nodePred)[2]

def getNodeIdFromPortPred(portPredicate):
	i1 = portPredicate.find('(')
	i2 = portPredicate.find(',')
	return portPredicate[i1 + 1 : i2]

def getPortId(portPredicate):
	portDescriptors = portPredicate.split(',')
	return portDescriptors[1]

def getGroupId(portPredicate):
	portDescriptors = portPredicate.split(',')
	return portDescriptors[2]

def getPortDirection(portPredicate):
	portDescriptors = portPredicate.split(',')
	return portDescriptors[3]

def getPortType(portPredicate):
	portDescriptors = portPredicate.split(',')
	rawOutput = portDescriptors[4]
	i = rawOutput.find(')')
	return rawOutput[:i]

def getEdge(edgePredicate):
	edgePorts = edgePredicate.split(',')[2:4]
	return '(' + edgePorts[0] + ',' + edgePorts[1]

def getLabelFromLabelPred(labelPred):
	i1 = labelPred.find(',')
	i2 = labelPred.find(')')
	return labelPred[i1 + 1 : i2]

def getLabelPredForModel(modelObj, label):
	return 'label(' + modelObj.modelId + ',' + label + ').\n'

def computeRelPathToModels(mainPath, modelsPath):
	absMainPath  = abspath(mainPath)
	absModelsPath = abspath(modelsPath)
	absMainDirPath = dirname(absMainPath)
	return relpath(absModelsPath, absMainDirPath)


# This creates a temp directory in the same directory as the file at filepath
def createTempDirectory(filePath):
	dirPath = dirname(abspath(filePath))
	tempPath = dirPath + '/' + state.get('tempDirPath') + '/'
	if exists(tempPath):
		removeTempDir(tempPath)
	os.makedirs(tempPath)
	return tempPath

# This basically does rm -rf on the temp directory at tempPath
def removeTempDir(tempPath):
	shutil.rmtree(tempPath, ignore_errors=True)

# This generates the path for the file where all labelled models will be outputted
def computeClassFilePath():
	inputFileAbsPath = state.get('inputFilePath')
	fileName = basename(inputFileAbsPath).split('.', 1)[0]
	fileDir  = dirname(inputFileAbsPath)
	rand = uuid.uuid4().hex[:5]

	return join(fileDir, fileName + '_classified_' + rand + '.pl')

# This generates a diagram for the component comp and opens it with the default
# image viewer; the outer black box delimit the component, the blue boxes delimit
# its port groups and the ports are the inner nodes; red ports are out, green ports
# are in, orange ports are inout
def generateCompDiagram(comp):
	tempDirPath = state.get('tempDirPath')
	rand = uuid.uuid4().hex
	indexTracker = {}
	g = Graph('G', filename=join(tempDirPath, rand + '.gv'), engine='fdp')
	g.format = 'png'

	with g.subgraph(name='clusterComponent') as c:
		for group in comp.groups:
			with c.subgraph(name='cluster' + uuid.uuid4().hex) as a:
				a.attr(color='blue')
				for port in group.ports:
					name = port.portType
					idx = 0
					if not (name in indexTracker):
						indexTracker[name] = 1
					else:
						idx = indexTracker[name]
						indexTracker[name] += 1
					if (port.direction == 'in'):
						a.node_attr.update(color='green', style='filled')
					elif (port.direction == 'out'):
						a.node_attr.update(color='red', style='filled')
					else:
						a.node_attr.update(color='orange')
					a.node(name + '_' + str(idx), label=name, style='filled')
	
	g.view()

# Converts list strs e.g. ['a', 'b', 'c'] to string 'a, b, c'
# PRE: len(strs) >= 2
def listAsEnumeratedString(strs):
	s = ''
	for i in range(len(strs) - 1):
		s += strs[i] + ', '
	s += strs[len(strs) - 1]
	return s

# This generates a diagram for the input model and opens it with the default
# image viewer; the outer black boxes delimit its components, the blue boxes delimit
# their port groups and the ports are the inner nodes; red ports are out, green ports
# are in, orange ports are inout
# Note that at the bottom of the diagram we also print the predicted label(s) for
# the model, if any such prediction is available in labelsForModel
def generateModelDiagram(model, labelsForModel):
	tempDirPath = state.get('tempDirPath')
	g = Graph('G', filename=join(tempDirPath, uuid.uuid4().hex + '.gv'), engine='fdp')
	g.format = 'png'

	for i in range(len(model.components)):
		comp = model.components[i]

		with g.subgraph(name='clusterComponent' + str(i)) as c:
			for group in comp.groups:
				with c.subgraph(name='cluster' + uuid.uuid4().hex) as a:
					a.attr(color='blue')
					for port in group.ports:
						name   = port.portType
						portId = port.portId
						if (port.direction == 'in'):
							a.node_attr.update(color='green', style='filled')
						elif (port.direction == 'out'):
							a.node_attr.update(color='red', style='filled')
						else:
							a.node_attr.update(color='orange')
						a.node(portId, label=name, style='filled')
			c.attr(label=comp.name)
			c.attr(fontsize='20')

	for edge in model.edges:
		portA = edge.getPortAId()
		portB = edge.getPortBId()
		g.edge(portA, portB)
	
	lStr = None
	if (not len(labelsForModel)):
		lStr = 'No predicted label available yet.'
	elif (len(labelsForModel) == 1):
		lStr = 'Predicted label: ' + labelsForModel[0]
	else:
		lStr = 'Predicted labels: ' + listAsEnumeratedString(labelsForModel)
	g.attr(label=lStr)

	g.view()

# Delete all of the temp directory and exit
def deleteTempDataAndExit():
	tempDirPath = state.get('tempDirPath')
	if (tempDirPath):
		removeTempDir(tempDirPath)
	try:
		sys.exit(0)
	except SystemExit:
		os._exit(0)

# This function gathers all labels the user will use for classification and
# returns them
def getAllLabelsFromUser():
	try:
		numOfLabels = int(input('Please specify the number of labels (at least 2): '))
		if (numOfLabels < 2):
			raise ValueError
	except ValueError:
		print('Provided invalid value, try again!')
		return getAllLabelsFromUser()

	labels = list()
	for i in range(numOfLabels):
		string = '* Label ' + str(i + 1) + ': '
		newLabel = input(string)
		if newLabel in labels:
			print('Provided duplicate labels, try again!')
			return getAllLabelsFromUser()
		else:
			labels.append(newLabel)
	return labels

# ILASP outputs hypothesis + time spent for pre-processing, solving, etc;
# This method trims this output and returns only the hypothesis
def getHypothesisfromILASPOutput(output):
	if 'UNSATISFIABLE' not in output:
		return output.split('Pre-processing', 1)[0]
	else:
		raise RuntimeError('Unfortunately, no hypothesis was found for at least one label.')

# This function updates hypotheses for label to newHyp
def updateHypothesis(label, newHyp):
	hypotheses = state.get('hypotheses')
	hypotheses[label] = newHyp

# This function takes the outputs of the concurrent ILASP runs and updates the
# hypotheses in the state
def updateHypotheses(outputs):
	for label in outputs.keys():
		hypStr = getHypothesisfromILASPOutput(outputs[label])
		updateHypothesis(label, hypStr)

def clustersAreEmpty(clusters):
	return len(clusters.keys()) == 0

# This function generates the context (custom background) for model
# This includes all of its components, ports and edges
# It also adds a predicate val(comp, V), which assigns a different bit to
# each component (represented by a different power of two in decimal system)
# This is used for ILASP list encoding to describe paths between components
def generateContext(model):
	contextStr = '\n'

	for compIdx in range(len(model.components)):
		comp = model.components[compIdx]
		contextStr += 'comp(' + comp.compId + ',' + comp.name + '). '
		contextStr += 'val('  + comp.compId + ',' + str(pow(2, compIdx)) + ').\n'

		for group in comp.groups:
			for port in group.ports:
				contextStr += 'port(' + comp.compId + ',' + port.portId + ').\n'

	for edge in model.edges:
		contextStr += 'edge' + str(edge) + '.\n'

	return contextStr

def generatePosExample(model):
	return '#pos({' + ILASP_LABEL_STRING + '}, {}, {' + generateContext(model) + '}).'

def generateNegExample(model):
	return '#pos({}, {' + ILASP_LABEL_STRING + '}, {' + generateContext(model) + '}).'

# Though it shouldn't ever be the case that we read an examples file not yet created,
# creating them initially in the temp directory is just a safety measure against crashes
def createLabelExampleFiles(labels):
	tempDirPath = state.get('tempDirPath')
	examplesPaths = {}
	for label in labels:
		examplesFileName = label + '_examples.las'
		labelExamplesPath = join(tempDirPath, examplesFileName)
		examplesPaths[label] = labelExamplesPath
		file = open(labelExamplesPath, 'w')
		file.close()
	return examplesPaths

# This creates ILASP file for label and writes fileStr to it, and returns
# its path
def createILASPProgram(label, fileStr):
	tempDirPath = state.get('tempDirPath')
	fileName = label + '_ILASP_program.las'
	programPath = join(tempDirPath, fileName)
	file = open(programPath, 'w')
	file.write(fileStr)
	file.close()
	return programPath

def getAbsPath(path):
	return abspath(path)

def getBackgroundPath():
	currDir = dirname(realpath(__file__))
	return abspath(join(currDir, 'background.las'))

def getBiasPath():
	currDir = dirname(realpath(__file__))
	return abspath(join(currDir, 'bias.las'))

# This returns contents of the background file as a string
def getBackgroundString():
	file = open(getBackgroundPath(), 'r')
	backgroundString = file.read()
	file.close()
	return backgroundString

# This returns contents of the bias file as a string
def getBiasString():
	file = open(getBiasPath(), 'r')
	biasString = file.read()
	file.close()
	return biasString

# This computes the bias component constants, which are the component types
def computeBiasConstants():
	constStr = ''
	compNames = list(state.get('componentNames'))
	for comp in compNames:
		constStr += '#constant(compC,' + comp + ').\n'
	return constStr

# This reads the file with examples for label and returns its contents as a string
def getExamplesString(label):
	examplesPath = state.get('labelExamplesPaths')[label]
	file = open(examplesPath, 'r')
	examplesStr = file.read()
	file.close()
	return examplesStr

# This function prints formatted hypotheses for all labels
def printHypotheses():
	hypotheses = state.get('hypotheses')
	labels     = state.get('labels')

	for labelId in range(len(labels)):
		label = labels[labelId]
		print("* Hypothesis for label '" + label + "':\n")
		if label in hypotheses.keys():
			hyp = hypotheses[label].replace(ILASP_LABEL_STRING, label)
			print(hyp)
		printSepLine(50)

		if labelId < (len(labels) - 1):
			print()

def trimModel(modelString):
	return "model" + modelString.strip()

# This function reads the contents of the input models file and returns a list
# with all model strings
def getModelsStrings(modelsPath):
	file = open(modelsPath)
	rawModels = file.read()
	file.close()
	return list(map(trimModel, rawModels.split("model")[1:]))

def getLabelPredStr(label):
	return 'label(M, ' + label + ')'

def getHypothesisWithFullModelPreds(hyp):
	newHyp = hyp

	for pred in PER_MODEL_PREDS:
		# E.g. turn ' comp(V0, gs)' into ' comp(M, V0, gs)'
		newHyp = newHyp.replace(' ' + pred + '(', ' ' + pred + '(M, ')

	if ':-' in newHyp:
		return newHyp.replace(':- ', ':- model(M), ')
	else:
		# This is the very specific case when only examples of one label
		# have been provided, so there exists only one non-trivial hypothesis,
		# namely, that label alone as a single rule.
		return newHyp.replace('.', ' :- model(M).')
	
	return newHyp.replace(' :- ', ' :- model(M), ')

# This function returns a string with all hypotheses aggregated for classification
# Note that multiple hypotheses may have used predicate invention, but used the
# same names for them, and we thus have to distinguish them as each one should
# be specific to their label's hypothesis only
def computeHypothesesString():
	invPreds = INVENTED_PREDICATES
	hypotheses = state.get('hypotheses')
	labels = hypotheses.keys()
	hypStr = ''

	for label in labels:
		labelHyp = hypotheses[label].replace(ILASP_LABEL_STRING, getLabelPredStr(label))
		labelHyp = getHypothesisWithFullModelPreds(labelHyp)

		for invPred in invPreds:
			labelInvPred = invPred + '_' + label
			if (invPred + '(') in labelHyp:
				labelHyp = labelHyp.replace(invPred + '(', labelInvPred + '(M, ')
			elif invPred in labelHyp:
				labelHyp = labelHyp.replace(invPred, labelInvPred + '(M)')

		hypStr += labelHyp + '\n'

	return hypStr

def setComponentName(comp, compIdToNameMap, prenamed, nameComponents):
	if (prenamed):
		if (comp.compId not in compIdToNameMap):
			raise ValueError('No name for ' + comp.compId + '!')
		comp.name = compIdToNameMap[comp.compId]
		state.get('componentNames').add(comp.name)

		return

	# if not prenamed:

	compTypes = state.get('componentTypes')
	try:
		idx = compTypes.index(comp)
		comp.name = compTypes[idx].name
	except ValueError:
		if nameComponents:
			generateCompDiagram(comp)
			comp.name = input(' - Found new component, please provide a name for it: ')
			print()
		else:
			unnamedTypesCounter = state.get('unnamedTypesCounter')
			comp.name = 'type' + str(unnamedTypesCounter)
			state.set('unnamedTypesCounter', unnamedTypesCounter + 1)
		compTypes.append(comp)

# This function takes a string representation of a model, as provided in the input
# file, and computes the model object from the string. If it encounters any new
# component types in the process, it appends them to the componentTypes list in
# the state; it also asks the user for a component name if they agreed to name them,
# generating a diagram of the component to aid them, or generates a generic name
# instead otherwise
def computeModelObjFromModelStr(modelStr):
	modelPredicates = list(map(str.strip, modelStr.split(".")))
	modelId         = getModelId(modelPredicates[0])
	nodePredicates  = list(filter(lambda pred: pred.startswith("node"), modelPredicates))
	portPredicates  = list(filter(lambda pred: pred.startswith("port"), modelPredicates))
	edgePredicates  = list(filter(lambda pred: pred.startswith("edge"), modelPredicates))

	prenamed = state.get('prenamedComponents')
	nameComponents = state.get('nameComponents')

	newModel = Model(modelId, list(), list())

	compIdToNameMap = {}
	nodeGroupsMap = {}

	for nodePred in nodePredicates:
		nodeId = getNodeIdFromNodePred(nodePred)
		if prenamed:
			try:
				nodeType = getNodeTypeFromNodePred(nodePred)
				compIdToNameMap[nodeId] = nodeType
			except IndexError:
				raise ValueError('No component name provided for ' + nodeId + '!')

		nodeGroupsMap[nodeId] = list()

	for edgePred in edgePredicates:
		newModel.edges.append(Edge(getEdge(edgePred)))

	for portPred in portPredicates:
		portId    = getPortId(portPred)
		nodeId    = getNodeIdFromPortPred(portPred)
		groupId   = getGroupId(portPred)
		direction = getPortDirection(portPred)
		portType  = getPortType(portPred)

		port = Port(portId, portType, direction)
		nodeGroups = nodeGroupsMap[nodeId]
		found = False
		for group in nodeGroups:
			if group.groupId == groupId:
				group.ports.append(port)
				found = True
				break
		if not found:
			newGroup = PortGroup(groupId, list([port]))
			nodeGroupsMap[nodeId].append(newGroup)

	for node in list(nodeGroupsMap.keys()):
		if len(nodeGroupsMap[node]) == 0:
			continue

		comp = Component(node, nodeGroupsMap[node])
		if newModel.usesComponent(comp):
			newModel.components.append(comp)
			setComponentName(comp, compIdToNameMap, prenamed, nameComponents)

	return newModel

def generateModelString(model):
	modelId  = model.modelId
	modelStr = '\nmodel(' + modelId + ').\n'

	for compIdx in range(len(model.components)):
		comp = model.components[compIdx]
		modelStr += 'comp(' + modelId + ',' + comp.compId + ',' + comp.name + '). '
		modelStr += 'val('  + comp.compId + ',' + str(pow(2, compIdx)) + ').\n'

		for group in comp.groups:
			for port in group.ports:
				modelStr += 'port(' + comp.compId + ',' + port.portId + ').\n'

	for edge in model.edges:
		modelStr += 'edge' + str(edge) + '.\n'

	return modelStr

# This function generates the clingo program to be run in order to classify a given
# model object, based on the hypotheses in the state; it then runs the clingo 
# command, parses the labels from its output and returns those labels
def computeLabelPredsForModels(models, tempFilePath):
	labels 		  = state.get('labels')
	classifProg   = getBackgroundString()
	hypothesesStr = computeHypothesesString()

	for modelObj in models:
		classifProg += generateModelString(modelObj) + '\n\n'

	classifProg += hypothesesStr
	classifProg += '#show label/2.'

	file = open(tempFilePath, 'w')
	file.write(classifProg)
	file.close()

	clingoCmd = list(GENERIC_CLINGO_CMD)
	clingoCmd.append(tempFilePath)

	out, err = Popen(clingoCmd, stdout=PIPE, stderr=PIPE, universal_newlines=True).communicate()
	# raise RuntimeError only if actual error, not warnings, have occured
	if 'ERROR' in err:
		raise RuntimeError('Error encountered while classifying models.')

	labelledModels = list(filter(lambda w: w.startswith('label'), out.split()))

	return labelledModels

def generatePieChart(labels, values, title=''):
	tempDirPath = state.get('tempDirPath')
	imgPath = join(tempDirPath, uuid.uuid4().hex + '.png')

	plt.pie(values, autopct='%.1f%%', startangle=270)
	plt.title(title)
	plt.legend(labels, loc="best")
	plt.axis('equal')
	plt.savefig(imgPath)
	plt.clf()

	# We don't use plt.show() because we get a weird error
	# plus Popen doesn't block current process
	Popen(["xdg-open", imgPath])

def getBlankLabelsCounter():
	labels = state.get('labels')
	counter = {
		NO_LABEL_STRING: 0,
		MULTIPLE_LABELS_STRING: 0
	}

	for label in labels:
		counter[label] = 0

	return counter

def printClusters():
	clusters       = state.get('clusters')
	clusterWeights = state.get('clusterWeights')
	clusterKeys    = list(clusters.keys())

	print('\nClusters:')
	for ck in clusterKeys:
		print(str(ck) + ': ' + str(list(map(lambda m: m.labels, clusters[ck]))))
		print(str(ck) + ' weight: ' + str(clusterWeights[ck]))
	print()

def initClusterWeights():
	clusters = state.get('clusters')
	clusterKeys = list(clusters.keys())
	weights = {}

	for ck in clusterKeys:
		weights[ck] = 1

	state.set('clusterWeights', weights)

def getRemainingModelsList():
	clusters = state.get('clusters')
	clusterKeys = list(clusters.keys())
	allModels = list()

	for ck in clusterKeys:
		allModels += clusters[ck]

	return allModels + state.get('skippedModels')

def computeLabelsForModelObj(modelObj, tempFilePath=''):
	labelsForModel = list()

	if(state.get('labelPredictionsUpdated')):
		labelsForModel = modelObj.labels
	else:
		tempFilePath = tempFilePath or join(state.get('tempDirPath'), uuid.uuid4().hex + '.las')
		labelPredsForModel = computeLabelPredsForModels([modelObj], tempFilePath)
		labelsForModel = list(map(getLabelFromLabelPred, labelPredsForModel))

	return labelsForModel

def addModelToLabelCluster(clusters, modelObj, label):
	if label in clusters:
		clusters[label].append(modelObj)
	else:
		clusters[label] = [modelObj]

def getModelLabelsMap(labelPredsForModels):
	modelLabelsMap = {}

	for lPred in labelPredsForModels:
		mId    = getArgsFromPred(lPred)[0]
		mLabel = getArgsFromPred(lPred)[1]

		if mId in modelLabelsMap:
			modelLabelsMap[mId].append(mLabel)
		else:
			modelLabelsMap[mId] = [mLabel]

	return modelLabelsMap

def computeLabelsForNewModels(allModels, newClusters, allModelsNum, lockR, lockW):
	tempDirPath      = state.get('tempDirPath')
	tempFilePath     = join(tempDirPath, uuid.uuid4().hex + '.las')
	maxModelsAtOnce  = MODELS_PER_CLASSIF_PROC

	while True:
		currModels = list()
		lockR.acquire()
		if (not len(allModels)):
			lockR.release()
			return

		numOfModels = min(maxModelsAtOnce, len(allModels))
		# print(numOfModels)
		for idx in range(numOfModels):
			currModels.append(allModels.pop())
		# print(len(modelsStrings))
		lockR.release()

		labelPredsForModels = computeLabelPredsForModels(currModels, tempFilePath)
		modelLabelsMap = getModelLabelsMap(labelPredsForModels)

		for modelObj in currModels:
			mId = modelObj.modelId
			if mId in modelLabelsMap:
				modelObj.updateLabels(modelLabelsMap[mId])

				lockW.acquire()
				if (len(modelLabelsMap[mId]) == 1):
					addModelToLabelCluster(newClusters, modelObj, modelLabelsMap[mId][0])
				else:
					addModelToLabelCluster(newClusters, modelObj, MULTIPLE_LABELS_STRING)

			else:
				modelObj.updateLabels(list())

				lockW.acquire()
				addModelToLabelCluster(newClusters, modelObj, NO_LABEL_STRING)
			
			printProgressBar(allModelsNum)

			lockW.release()

def updateClusters(newClusters):
	state.set('clusters', newClusters)

	clusterKeys         = list(newClusters.keys())
	newClusterWeights   = {}
	actualLabelsCounter = 0
	noLabelStr          = NO_LABEL_STRING
	multipleLabelsStr   = MULTIPLE_LABELS_STRING

	for ck in clusterKeys:
		if (ck != noLabelStr and ck != multipleLabelsStr):
			actualLabelsCounter += 1
			newClusterWeights[ck] = 1

	boostedWeight = actualLabelsCounter or 1

	if noLabelStr in newClusters:
		newClusterWeights[noLabelStr] = boostedWeight

	if multipleLabelsStr in newClusters:
		newClusterWeights[multipleLabelsStr] = boostedWeight

	state.set('clusterWeights', newClusterWeights)

def showExpectedLabelsDistribution():
	clusters          = state.get('clusters')
	userLabelCounters = state.get('userLabelCounters')
	labels            = state.get('labels')

	userLabels  = list(filter(lambda l: userLabelCounters[l] > 0, labels))
	clusterLabels = list(clusters.keys())

	allLabels = list(set(userLabels + clusterLabels))

	values = list()
	for l in allLabels:
		val = 0

		if l in userLabels:
			val += userLabelCounters[l]
		if l in clusterLabels:
			val += len(clusters[l])

		values.append(val)

	title = 'Expected labels distribution with current hypotheses'
	# print(allLabels)
	# print(values)

	generatePieChart(allLabels, values, title=title)

def checkAndRecluster():
	if(state.get('labelPredictionsUpdated')):
		return

	allModels    = getRemainingModelsList()
	allModelsNum = len(allModels)
	lockR = Lock()
	lockW = Lock()
	newClusters = {}
	initProgressBar()

	threads = list()
	for tIdx in range(CLASSIFICATION_THREADS):
		threads.append(Thread(target=computeLabelsForNewModels, 
							args=(allModels, newClusters, allModelsNum, lockR, lockW),
							daemon=True))

	printTitle('Recalibrating algorithm with new hypotheses, please wait.')
	
	for thread in threads:
		thread.start()

	for thread in threads:
		thread.join()

	updateClusters(newClusters)
	state.set('skippedModels', [])
	state.set('labelPredictionsUpdated', True)
	showExpectedLabelsDistribution()

def initUserLabelCounters():
	labels = state.get('labels')
	counters = {}

	for label in labels:
		counters[label] = 0

	state.set('userLabelCounters', counters)