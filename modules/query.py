from tkinter import *
import tkinter as tk

def getQueryFromUser(inputQuery):
    queryStr = ''

    def getTextAndExit():
        nonlocal queryStr
        queryStr = text.get("1.0", END).strip()
        root.destroy()

    def selectAll(event):
        text.tag_add(SEL, "1.0", END)
        text.mark_set(INSERT, "1.0")
        text.see(INSERT)
        return 'break'

    def highlightPatterns(event):
        def highlightPattern(pattern, tag, color, regexp=False, withoutLastChar=False):
            start = "1.0"
            end = END
            text.tag_delete(tag)

            text.mark_set("matchStart", start)
            text.mark_set("matchEnd", start)
            text.mark_set("searchLimit", end)

            count = tk.IntVar()
            while True:
                index = text.search(pattern, "matchEnd", "searchLimit", count=count, regexp=regexp)
                if (index == "" or count.get() == 0):
                    break
                text.mark_set("matchStart", index)
                text.mark_set("matchEnd", "%s+%sc" % (index, count.get() - int(withoutLastChar)))
                text.tag_add(tag, "matchStart", "matchEnd")
                text.tag_config(tag, foreground=color)

        highlightPattern(r"bla[\s]", "bla_space", "blue", regexp=True)
        highlightPattern("bla:", "bla_colon", "blue", withoutLastChar=True)
        highlightPattern(":-", "sep", "green")

    root = Tk()
    root.title("Query editor")

    frame = Frame(root, width=400, height=400)
    frame.pack(expand=True, fill=BOTH)
    frame.grid_propagate(False)
    frame.grid_rowconfigure(0, weight=1)
    frame.grid_columnconfigure(0, weight=1)

    text = Text(frame, wrap="word", relief="sunken")
    text.bind("<KeyRelease>", highlightPatterns)
    text.insert(END, inputQuery)
    text.pack(expand=True, fill=BOTH)
    text.grid(row=0, column=0, sticky="nsew")
    text.bind("<Control-Key-a>", selectAll)
    text.bind("<Control-Key-A>", selectAll)

    scrollbar = Scrollbar(frame, command=text.yview)
    scrollbar.grid(row=0, column=1, sticky='nsew')
    text['yscrollcommand'] = scrollbar.set

    button = Button(root, text="Run", command=getTextAndExit)
    button.pack(side=BOTTOM)

    root.mainloop()

    return queryStr

query = getQueryFromUser('Initial')
print(len(query))
