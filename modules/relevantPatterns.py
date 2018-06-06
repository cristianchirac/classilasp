from tkinter import *
import state
from CONSTANTS import *

def setRelevantPatterns():
	patternVars = {}

	def onExit():
		nonlocal patternVars
		relevantPatterns = []
		for pattern in list(patternVars.keys()):
			if patternVars[pattern].get():
				relevantPatterns.append(pattern)

		state.set('relevantPatterns', relevantPatterns)
		root.destroy()

	def onConfigure(event):
	    canvas.configure(scrollregion=canvas.bbox('all'))

	root = Tk()
	root.title("Relevant patterns")
	root.columnconfigure(0, weight=1)
	root.rowconfigure(1, weight=1)
	
	label = Label(root, text="Please select ONLY the relevant patterns for classification:\n")
	label.grid(row=0)

	canvas = Canvas(root, width=300, height=300)
	canvas.grid(row=1, column=0, sticky="nsew")

	scrollbar = Scrollbar(root, command=canvas.yview)
	scrollbar.grid(row=1, column=1, sticky='nsew')

	canvas.configure(yscrollcommand = scrollbar.set)
	canvas.bind('<Configure>', onConfigure)

	frame = Frame(canvas)
	canvas.create_window((0,0), window=frame, anchor='nw')

	allPatterns = list(PATTERNS_SIGANTURES.keys())

	for idx in range(len(allPatterns)):
		pattern = allPatterns[idx]
		patternVars[pattern] = IntVar()
		patternText = " " + PATTERNS_SIGANTURES[pattern]
		Checkbutton(frame, text=patternText, variable=patternVars[pattern]).grid(row=idx, sticky=W)

	button = Button(root, text="Ok", command=onExit)
	button.grid(row=2)

	root.mainloop()
