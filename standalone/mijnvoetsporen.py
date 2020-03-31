import os
import platform
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import uuid
from tqdm import tqdm
import re
import datetime
from collections import Counter
import csv
from dateutil.parser import parse
import zipfile
import sys
from urllib.parse import urljoin, urlparse


WINDOWSIZE = (800, 500)
regex_left = r'[\u0000-\u001F\u0100-\uFFFF]?'
regex_datetime = r'[^\w]?([0-9./\-]{6,10},?[\sT][0-9:]{5,8}\s?[AP]?M?)[^\w]?\s?[\-\–]?\s'
regex_right = r'(([^:]+):\s)?(.*)'
regex_url = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
regex_message = re.compile(f'^{regex_left}{regex_datetime}{regex_right}$')
MAX_EXPORTED_MESSAGES = 1000000
names_urls = "news_list.csv"
word_window = 100
days_before = 3
days_after = 3


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    if platform.platform() == "Windows":
        return relative_path
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)




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
        
        self.maincanvas = tk.Canvas(self.frame1, width = windowsize[0], height = windowsize[1], background = "#5a8faa", borderwidth = 0, 
        highlightthickness = 0)
        self.maincanvas.pack()

        logo = tk.PhotoImage(data=open(resource_path("logo_small.gif"), mode='rb').read(), master = self.maincanvas)
        self.maincanvas.create_image(400, 20, anchor = tk.NW, image = logo)

        self.log = tk.Text(self.frame2, height=12, width = 110, bg = "#c3c2cb",  highlightthickness = 0)
        S = tk.Scrollbar(self.frame2, highlightbackground = "#c3c2cb")
        S.pack(side=tk.RIGHT, fill=tk.Y)
        self.log.pack(side=tk.LEFT, fill=tk.Y)
        S.config(command=self.log.yview)
        self.log.config(yscrollcommand=S.set)
        self.log.insert(tk.END, "Van harte welkom.\n")
        
        button2 = tk.Button(text='Kies je WhatsApp-bestand',command=self.whatsapp, bg = "#c3c2cb",  highlightthickness = 0, highlightbackground = "#5a8faa")

        
        self.maincanvas.create_window(100,40, window=button2)

        self.frame1.pack()
        self.frame2.pack()
        self.root.mainloop()
    
    def anonymize(self, data):
        '''
        This function takes the parsed WhatsApp data as input and anonymizes it
        At the moment: removing names and phone numbers, finding URLs, extracting words before and after URLs
        Matching URLs of the other person against whitelist, removing parameters from all URLs
        Still todo: Words of the other person matched against list of common words, whitelist of URLs should also include
        international sources
        '''
        with open(resource_path(names_urls), newline='') as f:
            reader = csv.reader(f)
            URL_list = [item for sublist in list(reader) for item in sublist]

        data_anonymized = data
        try: 
            for sublist in data_anonymized:
                #find URLs, put them in separate column, remove phone numbers (@mentions), hash names
                result = re.search(regex_url, sublist[4]).group() if re.search(regex_url, sublist[4]) != None else ""
                sublist[4] = re.sub(regex_url, "", sublist[4])
                sublist[4] = re.sub(r'@\d+', '', sublist[4])
                sublist.append(result)
                sublist[2] = hash(sublist[2])
                #Whitelist URLs for third parties, remove parameters
                try:
                    if sublist[3] is False:
                        if sublist[5] == "":
                            pass
                        elif isinstance(sublist[5], list):
                            newlist = []
                            for item in sublist[5]: 
                                if any(f in item for f in URL_list):
                                    newlist.append(item)
                                else: 
                                    newlist.append("WHITELISTED")
                            sublist[5] = newlist
                        elif any(f in sublist[5] for f in URL_list):
                            sublist[5] = urljoin(sublist[5], urlparse(sublist[5]).path)
                            pass
                        else:
                            sublist[5] = "WHITELISTED"
                    else:
                        if sublist[5] != "":
                            sublist[5] = urljoin(sublist[5], urlparse(sublist[5]).path)
                        else: 
                            pass
                except Exception as e:
                    self.log.insert(tk.END, e)
                else:
                    pass
                #Find text within a window before and after (based on word count + date), make BOW out of it
                if sublist[5] != "":
                    text_before = ""
                    cutoff = sublist[0] - datetime.timedelta(days = days_before)
                    text_after = "" 
                    cutoff2 = sublist[0] + datetime.timedelta(days = days_after)
                    for sublist2 in data_anonymized:
                        if cutoff <=  sublist2[0] <= sublist[0]:  
                            text_before += " " + sublist2[4]
                        elif sublist[0] < sublist2[0] <= cutoff2:
                            text_after += " " + sublist2[4] 
                        else:
                            pass
                    if len(text_before) > word_window:       
                        text_before = dict(Counter(text_before.split()[-word_window:])) 
                    else: 
                        text_before = dict(Counter(text_before.split()))
                    if len(text_after) > word_window: 
                        text_after = dict(Counter(text_after.split()[:word_window]))
                    else: 
                        text_after = dict(Counter(text_after.split()))
                    sublist.append(text_before)
                    sublist.append(text_after)             
                else:              
                    text_before = ''      
                    text_after = '' 
                    sublist.append(text_before)
                    sublist.append(text_after)   
            for sublist in data_anonymized: 
                del sublist[4]
        except Exception as e: 
             self.log.insert(tk.END, e)
        return data_anonymized

    def whatsapp(self):
        '''
        This function takes the raw WhatsApp data as input and parses it
        Still todo: moving this part into another script
        '''
        #Have participant retrieve the filename(s) and ask for their name (important for anonymizing properly)
        filename =  list(filedialog.askopenfilenames(initialdir = ".",title = "Select file"))
        filename_final = []
        n = 0 
        try: 
            for item in filename: 
                if item.endswith('.zip'):
                    zipdata = zipfile.ZipFile(item)
                    zipinfos =zipdata.infolist()
                    for zipinfo in zipinfos: 
                        n += 1
                        if os.path.exists(os.path.join(os.path.dirname(filename[0]), zipinfo.filename)):
                            zipinfo.filename = zipinfo.filename[:5] + str(n) + zipinfo.filename[5:]
                        else: 
                            pass
                        filename_final.append(os.path.join(os.path.dirname(filename[0]), zipinfo.filename))
                        zipdata.extract(zipinfo, path = os.path.join(os.path.dirname(filename[0])))
                else:
                    filename_final.append(item)
        except Exception as e: 
            self.log.insert(tk.END, e)
        self.log.insert(tk.END, "Je hebt de volgende bestanden gekozen voor je Whatsapp-takeout: {}\n\n".format(filename_final))
        try: 
            own_name = simpledialog.askstring("Input", "Welke naam gebruik je in WhatsApp?",parent=self.root)
        except Exception as e: 
            self.log.insert(tk.END, e)
        #Make new directory where the output files will be saved and let user know where they will be saved
        try:
            newpath = os.path.join(os.path.dirname(filename_final[0]), "footprint_data")
            if not os.path.exists(newpath):
                os.mkdir(os.path.join(newpath))
            self.log.insert(tk.END, "Jouw bestanden worden opgeslagen in de map : {}\n".format(newpath))
        except Exception as e: 
            newpath = " "
            self.log.insert(tk.END, e)
        #Parse the WhatsApp data
        data = []
        text = None
        try: 
            for file in filename_final: 
                count = len(open(file, encoding = 'utf8').readlines(  )) 
                conversation_id = uuid.uuid4().hex
                participants = set()
                conversation_data = []
                with open(file, encoding = 'utf8') as f: 
                    for line in tqdm(f, total=count):
                        matches = regex_message.search(line)
                        if matches is None:
                            if text is None:
                            # We are expecting the first message but could not successfully parse line
                                pass
                            else:
                                # We are parsing a multi-line message, add whole line to existing messages and continue with next line
                                text += '\n' + line.strip()
                                continue
                        try:
                            groups = matches.groups()
                        except Exception as e:
                            self.log.insert(tk.END, e)
                        if groups[2] is None:
                        # sender name is missing but otherwise fits the pattern. Assumed to be app info.
                            continue
                        try:
                        # get timestamp of message
                            new_timestamp = parse(groups[0])
                        except ValueError:
                        # Datetime could not be parsed
                            text += '\n' + line.strip()
                            continue
                        if text:
                        # Dump previous entry
                            conversation_data += [[timestamp, conversation_id, sender_name, outgoing, text]]
                    # set timestamp
                        timestamp = new_timestamp
                    # add other senders to participants
                        sender_name = groups[2]
                        if sender_name != own_name:
                            participants.add(sender_name)
                        outgoing = sender_name == own_name
                        text = groups[3].strip()
                # dump last line
                    if text and sender_name:
                        conversation_data += [[timestamp, conversation_id, sender_name, outgoing, text]]
                    data.extend(conversation_data)
        except Exception as e: 
            self.log.insert(tk.END, "This is the error: {}".format(e))
        #Write raw file and anonymized file
        try:
            header = ['date','conversation_id', 'author','from_self','message']
            with open(os.path.join(newpath, "processed_whatsapp_raw.csv"), "w", newline="", encoding = "utf8") as f:
                writer = csv.writer(f)
                writer.writerow(header)
                writer.writerows(data) 
            data_anonymized = self.anonymize(data)
            header_a = ['date','conversation_id', 'author','from_self', 'URL', 'text_before', 'text_after']
            with open(os.path.join(newpath, "processed_whatsapp_final.csv"), "w", newline="", encoding = "utf8") as f:
                writer = csv.writer(f)
                writer.writerow(header_a)
                writer.writerows(data_anonymized) 
        except Exception as e: 
            self.log.insert(tk.END, "{}".format(e))



if __name__ == "__main__":
    mijnvoetspoor = Mijnvoetsporen(WINDOWSIZE)