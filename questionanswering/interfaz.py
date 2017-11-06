import tkinter as tk
from tkinter import ttk
from ttkthemes import ThemedStyle
import dill as pickle
import json
import spacy
import sys

filename = 'Model/model'
f = open(filename, 'rb')
model = pickle.load(f)
f.close()

nlp = spacy.load('es_default', parser=False)
model.nlp_api = nlp
model.pExtractor.nlp_api = nlp
model.eExtractor.nlp_api = nlp 

top = tk.Tk()

style = ThemedStyle(top)
style.set_theme("arc")

top.grid_columnconfigure(2, weight=1)
top.resizable(width=False, height=True)
top.title('Question Answering')
#style = ttk.Style()
#style.configure("BW.TLabel", foreground="black", background="white")
L1 = tk.Label(top, text="Pregunta")
E1 = ttk.Entry(top, width=50)
L2 = tk.Label(top, text="keywords")
E2 = ttk.Entry(top, width=50)


L1.grid(row=1,column=1,padx=10,pady=5)
L2.grid(row=2,column=1,padx=10,pady=5)
E1.grid(row=1,column=2)
E2.grid(row=2,column=2)


labelframe = tk.Frame(top)
labelframe.grid(row=6,column=1,columnspan=2,sticky='w',padx=5)

left2 = tk.Label(labelframe, text="Respuetas")
left2.grid(row=7,column=1,sticky='w',pady=5,columnspan=2)
def helloCallBack():
	quest = E1.get()
	keys = E2.get()
	dict_log = model.answer_question(quest,keys,log=True)
	answer_type = dict_log.get("answer_type","")
	entity = dict_log.get("entity","")
	properti = dict_log.get("property","")
	answers = dict_log.get("answers","")
	left = tk.Label(labelframe, text="Tipo \n" + answer_type)
	
	left.grid(row=9,column=1,sticky='w',pady=5)
	
	left2 = tk.Label(labelframe, text="Entidades \n"+entity)
	left2.grid(row=11,column=1,sticky='w',pady=5)

	left3 = tk.Label(labelframe, text="Propiedad \n" +properti)
	left3.grid(row=13,column=1,sticky='w',pady=5)

	left4 = tk.Label(labelframe, text="Respuetas \n" +answers)
	left4.grid(row=15,column=1,sticky='w',pady=5)
	
	#left4 = Label(labelframe, text="Query: \n\n" + resp[3],justify=LEFT)
	#left4.grid(row=10,column=1,sticky='w',pady=10)
	

B = ttk.Button(top, text ="Respuesta", command = helloCallBack)
B.grid(row=3,column=2,sticky='e',padx=10)

top.minsize(width=500, height=500)
top.mainloop()