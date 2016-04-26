import tkinter as tk   # python3
from PIL import Image, ImageTk
#import Tkinter as tk   # python
from chord_node import *
from bootstrapping import *
from communication_layer import *
from middleware import *

TITLE_FONT = ("Helvetica", 18, "bold")

class SampleApp(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        # the container is where we'll stack a bunch of frames
        # on top of each other, then the one we want visible
        # will be raised above the others
        self.title("HashKittens")
        self.geometry("400x480+300+300")

        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        # When add new page into application
        # should also add it in this set
        for F in (MainPage, NewTaskPage, ResultPage):
            page_name = F.__name__
            frame = F(container, self)
            self.frames[page_name] = frame

            # put all of the pages in the same location;
            # the one on the top of the stacking order
            # will be the one that is visible.
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("MainPage")

    def show_frame(self, page_name):
        # Show a frame for the given page name
        frame = self.frames[page_name]
        frame.tkraise()


class MainPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label_blank = tk.Label(self)
        label_blank.pack(side="top", fill="both", pady="40")

        label_welcome = tk.Label(self, text="HashKittens", font=TITLE_FONT)
        label_welcome.pack(side="top", fill="both")

        kitten_image_jpg = Image.open("./res/kitten.png")
        kitten_image = ImageTk.PhotoImage(kitten_image_jpg)
        label_kitten_img = tk.Label(self, image=kitten_image)
        label_kitten_img.image = kitten_image
        label_kitten_img.pack(pady="10")

        label_blank1 = tk.Label(self)
        label_blank1.pack(side="top", fill="both", pady="20")

        start_button = tk.Button(self, text="START NEW", width=25,
                            command=lambda: controller.show_frame("NewTaskPage"))

        join_button = tk.Button(self, text="Join NOW", width=25,command=lambda: self.joinNetwork())
        result_button = tk.Button(self, text="Result(won't be here)", width=25,
                                  command=lambda: controller.show_frame("ResultPage"))

        start_button.pack()
        join_button.pack()
        result_button.pack()

    def joinNetwork(self):
        #trying to join network; do bootstrapping things
        peerIP, peerTimes, peerRecordID = getPeerIP()

        #get public IP address
        url = 'http://ip.42.pl/raw'
        data = ""
        headers = ""
        r = requests.get(url, data=data, headers=headers)
        ip = str(r.text)    
                    
        #connect to peer

        params = [""]
        i = 0
        while i < len(peerIP):
                try:
                        if ip != peerIP[i]:
                                print("Trying IP Address " + peerIP[i])
                                s = socket(AF_INET, SOCK_STREAM)
                                s.connect((peerIP[i], 838))
                                print("Got a connection!")
                                params = ["-l " + peerIP[i]]
                                break
                        else:
                                print ("This node was in the list. Removing and trying next.")
                                removeIPRecord(peerRecordID[i])
                                i = i+1
                except Exception as err:
                        print ("Peer " + str(i) + " unsuccessful. Trying next...")
                        removeIPRecord(peerRecordID[i])
                        if i == len(peerIP)-1:
                                print ("All peers tried. Something is wrong. ")
                                break                            
                        else:
                                i = i+1
                
        if len(peerIP) > 5:
               removeOldestIPEntry()
        postHostIP(ip)
        

        connectThread = Thread(target=mainChord, args=(params)) 
        connectThread.daemon = False
        connectThread.start()


class NewTaskPage(tk.Frame):


    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.listenThread = None
        label = tk.Label(self, text="Crack a New Hash", font=TITLE_FONT)
        label.pack(side="top", fill="x", pady=10)

        # hash type
        hash_container = tk.Frame(self)
        hash_container.pack(side="top", fill="x", pady=5)
        label_hash_content = tk.Label(hash_container, text="Hash Type:   ")
        label_hash_content.pack(side="left", fill="x")
        hash_type_var = tk.StringVar(hash_container)
        option = tk.OptionMenu(hash_container, hash_type_var, "NTLM")
        option.configure(width=40)
        option.pack(side="left", fill="x")

        # hash length
        hash_container = tk.Frame(self)
        hash_container.pack(side="top", fill="x", pady=5)
        label_hash_content = tk.Label(hash_container, text="Password Length: ")
        label_hash_content.pack(side="left", fill="x")
        hash_length_text = tk.StringVar()
        hash_content = tk.Entry(hash_container, textvariable=hash_length_text, bg="white", width=34)
        hash_content.pack(side="left", fill="x")

        # Char Set
        hash_container = tk.Frame(self)
        hash_container.pack(side="top", fill="x", pady=5)
        label_hash_content = tk.Label(hash_container, text="Char Set:      ")
        label_hash_content.pack(side="left", fill="x")
        char_set_var = tk.StringVar(hash_container)
        option = tk.OptionMenu(hash_container, char_set_var, "lower", "UPPER", "tOgGlE")
        option.configure(width=40)
        option.pack(side="left", fill="x")

        # hash
        hash_container = tk.Frame(self)
        hash_container.pack(side="top", fill="x", pady=5)
        label_hash_content = tk.Label(hash_container, text="Hash:             ")
        label_hash_content.pack(side="left", fill="x")
        hash_text = tk.StringVar();
        hash_content = tk.Entry(hash_container, textvariable=hash_text, bg="white", width=40)
        hash_content.pack(side="left", fill="x")

        # start button and back button
        # start_hashkittens() is the function to be called when clicking the button
        # this is an example of get input value and print it through a bind function
        start_button = tk.Button(self, text="START", width=25,
                                 command=lambda: self.start_hashkittens(hash_type_var.get(), hash_length_text.get(), char_set_var.get(), hash_text.get()))
        start_button.pack(side="top", fill="x")
        back_button = tk.Button(self, text="BACK", width=25,
                           command=lambda: controller.show_frame("MainPage"))
        back_button.pack(side="top", fill="x")

    def start_hashkittens(self, hash_type_var, hash_length, char_set_var, hash_text):
        #get node from DNS
        peerIP, peerTimes, peerRecordID = getPeerIP()
        #create message, send to peerIP[0]
        ni.ifaddresses('eth0')
        ip = ni.ifaddresses('eth0')[2][0]['addr']
        hashItem = hashSubmission(ip, peerIP[0], hash_type_var, hash_text, hash_length, char_set_var)
        firstNode = chordNode()
        firstNode.IpAddress = peerIP[0]
        firstNode.port = 838
        submitToNetwork(firstNode, hashItem)

        #client needs to wait for answer
        #Start listener thread
        print ("Waiting for password for hash: " + str(hashItem.hashtext))
        if self.listenThread is None:
                self.listenThread = Thread(target=client_listener, args=(ip,rpc_handler))
                self.listenThread.daemon = False
                self.listenThread.start()
        

class ResultPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(self, text="This is result page", font=TITLE_FONT)
        label.pack(side="top", fill="x", pady=10)
        button = tk.Button(self, text="Go to the start page",
                           command=lambda: controller.show_frame("MainPage"))
        button.pack()


if __name__ == "__main__":
    app = SampleApp()
    app.mainloop()
