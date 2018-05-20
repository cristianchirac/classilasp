state = {
	'mainScriptPath': '',
	'inputFilePath': '',
	'tempDirPath': '',

	'prenamedComponents': False,
	'nameComponents': False,
	'unnamedTypesCounter': 0,
	'componentTypes': [],
	'componentNames': set(),

	'iterationNum': 0,
	'numOfInputModels': 0,

	'labels': [],
	'labelExamplesPaths': [],
	'userLabelCounters': {},

	'skippedModels': [],
	'labelledModelIds': [],

	'prevQuery': '',
	'queryCache': [],

	'clusters': {},
	'clusterWeights': {},
	'mustLabelModels': [],

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