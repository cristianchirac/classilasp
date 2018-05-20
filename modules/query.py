from tkinter import *
import state
import utils
from constants import *
from os.path import *
from subprocess import PIPE, run, Popen
from threading import Thread, Lock

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
        highlightPattern(r"" + key + "[\s]", "spaces", "blue", regexp=True)
        highlightPattern(key + ":", "colon", "blue", withoutLastChar=True)
        highlightPattern(":-", "sep", "green")

        if (inputQuery != ''):
            labelVar.set("Query edited, cache will be updated.")

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

def getQueryRules(query):
    return list(filter(lambda r: r != '.', list(map(lambda r: r.strip() + '.', query.split('.')))))

def addSpaces(rule):
    newRule = rule
    seps = ['.', ',', ':-']
    for sep in seps:
        newRule = newRule.replace(sep, ' ' + sep + ' ')
    return ' ' + newRule + ' '

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
        if QUERY_KEY_HEAD in spacedRule[i:]:
            print("\n*** ALERT: '" + QUERY_KEY_HEAD + "' not allowed in rule body: '" + rule + "'")
            return False
    
    return True

def getRuleHead(rule):
    return rule.split(':-')[0].strip()

def computeGenericQuery(query):
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
            newRule = newRule.replace(' ' + head + '(', ' ' + head + '(M, ')
            newRule = newRule.replace(' ' + head + ' ', ' ' + head + '(M) ')
        for pred in PER_MODEL_PREDS:
            newRule = newRule.replace(' ' + pred + '(', ' ' + pred + '(M, ')
        newRule = newRule.replace(':-', ':- model(M), ')
        genericQuery += newRule + '\n'

    return genericQuery


def updateCache(query):
    genericQuery = computeGenericQuery(query)
    input()

def getModelFromCache():
    prevQuery  = state.get('prevQuery')
    queryCache = state.get('queryCache')

    query = getQueryFromUser(prevQuery)
    if (query == ''):
        return None

    if (query != prevQuery):
        if not checkQueryCorrectness(query):
            return None
        updateCache(query)

    if not len(queryCache):
        print('\n*** ALERT: cache is empty, please change query or select random model!')
        return None
    else:
        return queryCache.pop()

# query = getQueryFromUser('hello')
# print(len(query))
