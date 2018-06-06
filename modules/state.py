from CONSTANTS import *

state = {
	'mainScriptPath': '',
	'inputFilePath': '',
	'outputFilePath': '',
	'tempDirPath': '',

	'noise': False,

	'relevantPatterns': [],

	'prenamedComponents': False,
	'nameComponents': False,
	'unnamedTypesCounter': 0,
	'componentTypes': [],
	'componentNames': set(),

	'iterationNum': 0,
	'numOfInputModels': 0,

	'sampleModelIds': [],

	'labels': [],
	'labelExamplesPaths': {},
	'userLabelCounters': {},

	'skippedModels': [],
	'labelledModelIds': [],

	'prevQuery': '',
	'ranAQuery': False,
	'queryCache': [],

	'clusters': {},
	'clusterWeights': {},
	'mustLabelModels': {
		NO_LABEL_STRING:        [],
		MULTIPLE_LABELS_STRING: []
	},

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