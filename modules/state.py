state = {
	'mainScriptPath': '',
	'inputFilePath': '',
	'tempDirPath': '__temp__',

	'unnamedTypesCounter': 0,
	'iterationNum': 0,
	'numOfInputModels': 0,

	'componentTypes': [],

	'labels': [],
	'labelExamplesPaths': [],
	'userLabelCounters': {},

	'skippedModels': [],

	'clusters': {},
	'clusterWeights': {},

	'hypotheses': {},
	'hypothesesToUpdate': set(),

	'labelPredictionsUpdated': True,

	'classifOutput': ''
}

def set(key, value):
	state[key] = value

def get(key):
	try:
		return state[key]
	except KeyError:
		return None