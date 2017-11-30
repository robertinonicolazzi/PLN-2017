top = Tk()
top.grid_columnconfigure(2, weight=1)
top.resizable(width=False, height=False)
top.title('Question Answering')

L1 = Label(top, text="Pregunta")
E1 = Entry(top, bd =2,width=50)
L2 = Label(top, text="keywords")
E2 = Entry(top, bd =2,width=50)


L1.grid(row=1,column=1,padx=10,pady=5)
L2.grid(row=2,column=1,padx=10,pady=5)
E1.grid(row=1,column=2)
E2.grid(row=2,column=2)

labelframe = LabelFrame(top, text="Respueta")
labelframe.grid(row=6,column=1,columnspan=2,sticky='w',padx=5)

def helloCallBack():
	quest = E1.get()
	keys = E2.get()
	resp = answerTypeClass.answer_question(quest,keys)

	 
	left = Label(labelframe, text= "Tipo:       " + resp)
	
	padright = 500-10-len(resp)-14-95
	left.grid(row=7,column=1,sticky='w',padx=(0, padright))
	'''
	left2 = Label(labelframe, text="Entidad:  " + resp[1])
	left2.grid(row=8,column=1,sticky='w')

	left3 = Label(labelframe, text="Respuesta: " + resp[2])
	left3.grid(row=11,column=1,sticky='w',pady=5)

	left4 = Label(labelframe, text="Query: \n\n" + resp[3],justify=LEFT)
	left4.grid(row=10,column=1,sticky='w',pady=10)
	'''

B = Button(top, text ="Respuesta", command = helloCallBack)
B.grid(row=3,column=2,sticky='e',padx=10)

top.minsize(width=500, height=200)
top.mainloop()