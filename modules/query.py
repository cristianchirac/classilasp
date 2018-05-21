from tkinter import *
import state
import utils
import uuid
import random
from CONSTANTS import *
from os.path import *
from subprocess import PIPE, run, Popen
from threading import Thread, Lock

# This function's role is to obtain a query string from the user.
# It does so by creating a tkinter popup, with a Text widget and
# two buttons, "Run" and "Cancel", which function as they are
# expected to. The query string is stored in queryStr and returned
# when the user presses "Run"; if the user presses "Cancel" or X,
# the function returns an empty string
def getQueryFromUser(inputQuery):
    queryStr = ''

    def getTextAndExit():
        nonlocal queryStr
        queryStr = text.get("1.0", END).strip()
        root.destroy()

    def onCancel():
        nonlocal queryStr
        queryStr = ''
        root.destroy()

    def selectAll(event):
        text.tag_add(SEL, "1.0", END)
        text.mark_set(INSERT, "1.0")
        text.see(INSERT)
        return 'break'

    def onKeyRelease(event):
        def highlightPattern(pattern, tag, color, regexp=False, withoutLastChar=False):
            start = "1.0"
            end = END
            text.tag_delete(tag)

            text.mark_set("matchStart", start)
            text.mark_set("matchEnd", start)
            text.mark_set("searchLimit", end)

            count = IntVar()
            while True:
                index = text.search(pattern, "matchEnd", "searchLimit", count=count, regexp=regexp)
                if (index == "" or count.get() == 0):
                    break
                text.mark_set("matchStart", index)
                text.mark_set("matchEnd", "%s+%sc" % (index, count.get() - int(withoutLastChar)))
                text.tag_add(tag, "matchStart", "matchEnd")
                text.tag_config(tag, foreground=color)

        key = QUERY_KEY_HEAD
        # Highlight the instances of QUERY_KEY_HEAD, in order for the user to
        # be reassured against typos; also highlight ':-'
        highlightPattern(r"" + key + "[\s]", "spaces", "blue", regexp=True)
        highlightPattern(key + ":", "colon", "blue", withoutLastChar=True)
        highlightPattern(":-", "sep", "green")

        if (inputQuery != ''):
            labelVar.set("Editing query, press 'Run' when finished.")

    root = Tk()
    root.title("Query editor")

    labelVar = StringVar()
    label = Label(root, textvariable=labelVar)
    label.pack(side=TOP)
    if (inputQuery == ''):
        labelVar.set("Please type in your query, then hit 'Run'.")
    else:
        labelVar.set("Query unchanged, click 'Run' to get new model from cache.")

    frame = Frame(root, width=400, height=400)
    frame.pack(expand=True, fill=BOTH)
    frame.grid_propagate(False)
    frame.grid_rowconfigure(0, weight=1)
    frame.grid_columnconfigure(0, weight=1)

    bottomframe = Frame(root)
    bottomframe.pack(side=BOTTOM)

    text = Text(frame, wrap="word", relief="sunken")
    text.bind("<KeyRelease>", onKeyRelease)
    text.insert(END, inputQuery)
    text.pack(expand=True, fill=BOTH)
    text.grid(row=0, column=0, sticky="nsew")
    text.bind("<Control-Key-a>", selectAll)
    text.bind("<Control-Key-A>", selectAll)

    scrollbar = Scrollbar(frame, command=text.yview)
    scrollbar.grid(row=0, column=1, sticky='nsew')
    text['yscrollcommand'] = scrollbar.set

    runButton = Button(bottomframe, text="Run", command=getTextAndExit)
    runButton.pack(side=LEFT)
    cancelButton = Button(bottomframe, text="Cancel", command=onCancel)
    cancelButton.pack(side=RIGHT)

    root.mainloop()

    return queryStr

# Given a query string, return its (stripped) rules as a list
def getQueryRules(query):
    return list(filter(lambda r: r != '.', list(map(lambda r: r.strip() + '.', query.split('.')))))

# This adds spaces around the separators '.', ',' and ':-',
# and removes them from around parantheses; this will help
# with basic matching of predicate names
def addSpaces(rule):
    newRule = rule
    seps = ['.', ',', ':-']
    for sep in seps:
        newRule = newRule.replace(sep, ' ' + sep + ' ')

    while ' )' in newRule:
        newRule = newRule.replace(' )', ')')

    while '( ' in newRule:
        newRule = newRule.replace('( ', '(')

    return ' ' + newRule + ' '

# This function, as its name suggests, checks the correctness of a query.
# It does so by first running it with clingo; if that returns an error,
# then the user is alerted and the function returns False. Otherwise,
# the function then checks if all the query rules are of the form 
# "head :- body"; if not, it alerts the user and returns False.
# Finally, it checks that the QUERY_KEY_HEAD only appears as a head
# in all rules. Again, if this doesn't hold, the user is alerted and
# False is returned. Otherwise, the function returns True, as all
# checks have passed.
def checkQueryCorrectness(query):
    queryFilePath = join(state.get('tempDirPath'), QUERY_FILE_NAME)
    file = open(queryFilePath, 'w')
    file.write(query)
    file.close()

    clingoCmd = list(GENERIC_CLINGO_CMD)
    clingoCmd.append(queryFilePath)
    out, err = Popen(clingoCmd, stdout=PIPE, stderr=PIPE, universal_newlines=True).communicate()

    if 'ERROR' in err:
        print('\n*** ALERT: Syntax error in query.')
        return False

    queryRules = getQueryRules(query)
    spacedRules = list(map(addSpaces, queryRules))
    for idx in range(len(queryRules)):
        rule       = queryRules[idx]
        spacedRule = spacedRules[idx]

        if ':-' not in rule:
            print("\n*** ALERT: No rules without body allowed: '" + rule + "'")
            return False

        i = rule.index(':-')
        if (' ' + QUERY_KEY_HEAD + ' ') in spacedRule[i:]:
            print("\n*** ALERT: '" + QUERY_KEY_HEAD + "' not allowed in rule body: '" + rule + "'")
            return False
    
    return True

# Returns the head of a rule assumes to be of the form "head :- body"
def getRuleHead(rule):
    return rule.split(':-')[0].strip()

# Takes a query that is assumed to describe a model and generalizes it
# in the sense that, for example, all predicates with no args like "p"
# become "p(M)", where "M" is a variable for the model (read below for
# more info on that). This is because, if multiple models are run with
# the same query, these predicates need to hold PER MODEL, not for all
# or no models.
def computeGenericQuery(query):
    # mVar is the name of the model variable in the generic query.
    # Since the user will only use very simple variable names,
    # having a fixed 'random' variable name should be enough to
    # avoid any name conflicts
    mVar = 'M040b63b7'
    headPreds = set()

    rules = list(map(addSpaces, getQueryRules(query)))
    for rule in rules:
        head = getRuleHead(rule)
        if '(' in head:
            i = head.index('(')
            head = head[:i]
        headPreds.add(head)

    headPreds = list(headPreds)
    genericQuery = ''
    for rule in rules:
        newRule = rule
        for head in headPreds:
            newRule = newRule.replace(' ' + head + '(', ' ' + head + '(' + mVar + ', ')
            newRule = newRule.replace(' ' + head + ' ', ' ' + head + '(' + mVar + ') ')
        for pred in PER_MODEL_PREDS:
            newRule = newRule.replace(' ' + pred + '(', ' ' + pred + '(' + mVar +', ')
        newRule = newRule.replace(':-', ':- model(' + mVar + '), ')
        genericQuery += newRule + '\n'

    return genericQuery

# Given a list of model objects and a query (with they keyword QUERY_KEY_HEAD),
# this function computes an ASP program with the string representations
# for all models, as well as the (generic) query, then gathers all
# models for which the QUERY_KEY_HEAD holds, and returns those as a list
def getValidModels(models, query, tempFilePath):
    def getModelIdFromQueryPred(pred):
        i1 = pred.find('(')
        i2 = pred.find(')')
        return pred[i1 + 1 : i2]

    classifProg   = utils.getBackgroundString()
    for modelObj in models:
        classifProg += utils.generateModelString(modelObj) + '\n\n'

    classifProg += query + '\n\n'
    classifProg += '#show select/1.'

    file = open(tempFilePath, 'w')
    file.write(classifProg)
    file.close()

    clingoCmd = list(GENERIC_CLINGO_CMD)
    clingoCmd.append(tempFilePath)

    out, err = Popen(clingoCmd, stdout=PIPE, stderr=PIPE, universal_newlines=True).communicate()
    # raise RuntimeError only if actual error, not warnings, have occured
    if 'ERROR' in err:
        raise RuntimeError('Error encountered while classifying models.')

    validModelPreds = list(filter(lambda w: w.startswith(QUERY_KEY_HEAD), out.split()))
    validModelIds   = list(map(getModelIdFromQueryPred, validModelPreds))

    return list(filter(lambda m: m.modelId in validModelIds, models))

# This function is to be run by each thread in updateCache. As its name
# suggests, it pops MODELS_PER_PROC models from modelStrings, and uses
# getValidModels, along with query, to compute the models that are valid
# according to query. It then selects only those models that have not 
# already been (manually) labelled by the user, and adds them to the list
# validModels. All read and write operations of common data is performed
# thread-safely using the locks lockR and lockW. The function returns
# when modelStrings is empty.
def popModelsAndCheckQuery(modelStrings, query, lockR, lockW, validModels):
    tempDirPath      = state.get('tempDirPath')
    tempFilePath     = join(tempDirPath, uuid.uuid4().hex + '.las')
    totalNumOfModels = state.get('numOfInputModels')
    labelledModelIds = state.get('labelledModelIds')
    maxModelsAtOnce  = MODELS_PER_PROC

    while True:
        currModels = list()
        lockR.acquire()
        if (not len(modelStrings)):
            lockR.release()
            return

        numOfModels = min(maxModelsAtOnce, len(modelStrings))
        # print(numOfModels)
        for idx in range(numOfModels):
            currModels.append(modelStrings.pop())
        # print(len(modelStrings))
        lockR.release()

        modelObjs = list(map(utils.computeModelObjFromModelStr, currModels))
        validCurrModels = getValidModels(modelObjs, query, tempFilePath)
        nonLabelledModels = list(filter(lambda m: m.modelId not in labelledModelIds, validCurrModels))

        lockW.acquire()
        validModels.extend(nonLabelledModels)
        utils.printProgressBar(totalNumOfModels, numOfIterations=numOfModels)
        lockW.release()

# This function uses query to update the cache of models complying
# with it. It reads all models from the input file, then computes
# all valid models in a number of CLASSIFICATION_THREADS threads,
# then selects at most QUERY_CACHE_SIZE many models to put in the cache.
# It doesn't short-circuit after finding QUERY_CACHE_SIZE valid models
# in the input file because it accounts for positional biases in the file
# (e.g. models in the beginning of the file might be relatively "smaller"
# than the ones towards its end, since those are likely combinatorially 
# pre-generated)
def updateCache(query):
    genericQuery = computeGenericQuery(query)
    modelStrings = utils.getModelsStrings(state.get('inputFilePath'))
    utils.initProgressBar()
    numOfThreads = CLASSIFICATION_THREADS
    lockR = Lock()
    lockW = Lock()

    # validModels will contain all models 'valid' in the sense that they comply with
    # the query constraints, and are also not among the already labelled models
    validModels = list()

    threads = list()
    for tIdx in range(numOfThreads):
        threads.append(Thread(target=popModelsAndCheckQuery, 
                            args=(modelStrings, genericQuery, lockR, lockW, validModels),
                            daemon=True))
    utils.printTitle('Searching for complying models, this might take a while.')
    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    randomSampleSize = min(len(validModels), QUERY_CACHE_SIZE)
    cache = random.sample(validModels, randomSampleSize)
    state.set('queryCache', cache)

    # Update preQuery to have it appear by default in the query editor
    # next time the user wants to use it
    state.set('prevQuery', query)

# This function's role is to obtain a model complying with a query
# provided by the user. First, it gets that query; if the query is
# empty, it returns None. If the query is different from the previous
# one (initially ''), it checks its correctness; if that fails, returns
# None. Otherwise, update the cache by searching all complying models
# and adding the required number to the cache. If the cache is empty,
# alert the user and return None. Otherwise, pop a model from the cache
# (assumed to be randomly ordered) and return that model.
def getModelWithQuery():
    prevQuery  = state.get('prevQuery')

    query = getQueryFromUser(prevQuery)
    if (query == ''):
        return None

    if (query != prevQuery):
        if not checkQueryCorrectness(query):
            return None
        updateCache(query)

    queryCache = state.get('queryCache')
    if not len(queryCache):
        print('\n*** ALERT: cache is empty, please change query or select random model!')
        return None
    else:
        return queryCache.pop()

# query = getQueryFromUser('hello')
# print(len(query))
