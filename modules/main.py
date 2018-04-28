#!/usr/bin/env python

# IMPORTS
import sys
import os
import traceback

import state
import utils
import preProcessing
import postProcessing
import classifyModels

# PRE-PROCESSING BIT
def preProcessingFunc():
	mainScriptPath = sys.argv[0]

	try:
		inputFilePath = sys.argv[1]
	except IndexError:
		raise RuntimeError('No file with unclassified models provided!')

	state.set('mainScriptPath', utils.getAbsPath(mainScriptPath))
	state.set('inputFilePath', utils.getAbsPath(inputFilePath))

	utils.printTitle('Pre-processing of given file is about to begin.')
	tempDirPath = utils.createTempDirectory(mainScriptPath)
	state.set('tempDirPath', tempDirPath)

	nameComponentsInput = None
	while(nameComponentsInput != 'y' and nameComponentsInput != 'n'):
		nameComponentsInput = input('Would you like to ' +
									'name the components for more human-readable class hypotheses? ' +
									'(y/n) ').lower()
	nameComponents = nameComponentsInput == 'y'

	clustersMap = preProcessing.parseInputFile(nameComponents)
	state.set('clusters', clustersMap)

	utils.printTitle('Pre-processing of file complete!')

	labels             = utils.getAllLabelsFromUser()
	labelExamplesPaths = utils.createLabelExampleFiles(labels)

	state.set('labels', labels)
	state.set('labelExamplesPaths', labelExamplesPaths)

	utils.printTitle('Thank you, classification process will now begin.')

# ACTUAL PROCESSING CYCLE
def processingCycleFunc():
	classifyModels.computeHypotheses()

# POST-PROCESSING FOR CLASSIFYING ALL INITIAL DATA, CLEARING AND CLOSING USED RESOURCES
def postProcessingFunc():
	modelsAbsPath = state.get('inputFilePath')
	classifiedDataFilePath = postProcessing.classifyAllModels(modelsAbsPath)

def main():
	preProcessingFunc()
	while True:
		processingCycleFunc()
		postProcessingFunc()
		print('Would you like to:')
		print('(1) Continue classification to improve the class hypotheses?')
		print('(2) Exit?')
		while True:
			try:
				ans = int(input('Your answer (1/2): '))
				if (ans < 1 or ans > 2):
					raise ValueError
				break
			except ValueError:
				continue
		if (ans == 2):
			break
		else:
			print()

if __name__ == "__main__":
    try:
    	main()
    except KeyboardInterrupt:
        print('\nInterrupted from keyboard!\n')
    except Exception:
    	traceback.print_exc()
    finally:
    	utils.deleteTempDataAndExit()