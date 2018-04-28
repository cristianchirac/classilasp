state = {
	'mainScriptPath': '',
	'inputFilePath': '',
	'tempDirPath': '',
	'unnamedTypesCounter': 1,
	'iterationNum': 0,
	'numOfInputModels': 0,
	'componentTypes': [],
	'labels': [],
	'labelExamplesPaths': [],
	'clusters': {},
	'clusterWeights': {},
	'hypotheses': {},
	'hypothesesToUpdate': set(),
	'classifOutput': ''
}

def set(key, value):
	state[key] = value

def get(key):
	try:
		return state[key]
	except KeyError:
		return None