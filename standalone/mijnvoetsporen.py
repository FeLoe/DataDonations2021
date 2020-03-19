import tkinter as tk
from tkinter import filedialog, messagebox

WINDOWSIZE = (640, 480)



class Mijnvoetsporen():
    def __init__ (self, windowsize, personalized_name="Jouw"):
        ''' 
        bla bla

        windowsize  tuple (width, height)

        '''
        self.root = tk.Tk()
        self.frame1 = tk.Frame(self.root)
        self.frame2 = tk.Frame(self.root)
        self.root.title("{} digitale voetsporen".format(personalized_name))
        
        self.maincanvas = tk.Canvas(self.frame1, width = windowsize[0], height = windowsize[1])
        self.maincanvas.pack()

        logo = tk.PhotoImage(file="logo_small.gif", master = self.maincanvas)
        self.maincanvas.create_image(400, 20, anchor = tk.NW, image = logo)

        self.log = tk.Text(self.frame2, height=8, width = 80)
        S = tk.Scrollbar(self.frame2)
        S.pack(side=tk.RIGHT, fill=tk.Y)
        self.log.pack(side=tk.LEFT, fill=tk.Y)
        S.config(command=self.log.yview)
        self.log.config(yscrollcommand=S.set)
        self.log.insert(tk.END, "Van harte welkom.\n")
        
        button1 = tk.Button(text='Click Me',command=self.hello, bg='brown',fg='white')
        button2 = tk.Button(text='Kies je WhatsApp-bestand',command=self.whatsapp, bg='brown',fg='white')

        
        self.maincanvas.create_window(40,40, window=button1)
        self.maincanvas.create_window(100,40, window=button2)

        self.frame1.pack()
        self.frame2.pack()
        self.root.mainloop()

    def hello(self):  
        label1 = tk.Label(self.root, text= 'Hello World!', fg='green', font=('helvetica', 12, 'bold'))
        self.maincanvas.create_window(150, 200, window=label1)

    def whatsapp(self):
        # filename =  filedialog.askopenfilename(initialdir = ".",title = "Select file",filetypes = (("all files","*.*"), ("json files","*.json")))
        filename =  filedialog.askopenfilename(initialdir = ".",title = "Select file")
        #messagebox.showinfo("File selected", "You selected {} as your WhatsApp takeout file".format(filename))
        self.log.insert(tk.END, "Je hebt het volgende bestand gekozen voor je Whatsapp-takeout: {}\n".format(filename))


if __name__ == "__main__":
    mijnvoetspoor = Mijnvoetsporen(WINDOWSIZE)
