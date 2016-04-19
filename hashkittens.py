import tkinter as tk   # python3
from PIL import Image, ImageTk
#import Tkinter as tk   # python
from middleware import *
from chord_node import *
from bootstrapping import *
from communication_layer import *

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
        for F in (MainPage, NewTaskPage, JoinPage, ResultPage):
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
        join_button = tk.Button(self, text="JOIN", width=25,
                            command=lambda: controller.show_frame("JoinPage"))
        result_button = tk.Button(self, text="Result(won't be here)", width=25,
                                  command=lambda: controller.show_frame("ResultPage"))

        start_button.pack()
        join_button.pack()
        result_button.pack()


class NewTaskPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        label_blank1 = tk.Label(self)
        label_blank1.pack(side="top", fill="both", pady="3")

        label = tk.Label(self, text="Crack a New Hash", font=TITLE_FONT)
        label.pack(side="top", fill="x", pady=10)

        label_blank1 = tk.Label(self)
        label_blank1.pack(side="top", fill="both", pady="3")

        # hash type
        hash_container = tk.Frame(self)
        hash_container.pack(side="top", pady=5)
        label_hash_content = tk.Label(hash_container, text="Hash Type:   ")
        label_hash_content.pack(side="left")
        hash_type_var = tk.StringVar(hash_container)
        option = tk.OptionMenu(hash_container, hash_type_var, "NTLM")
        option.configure(width=40)
        option.pack(side="left")

        # hash length
        hash_container = tk.Frame(self)
        hash_container.pack(side="top", pady=5)
        label_hash_content = tk.Label(hash_container, text="Password Length: ")
        label_hash_content.pack(side="left")
        hash_length_text = tk.StringVar()
        hash_content = tk.Entry(hash_container, textvariable=hash_length_text, bg="white", width=36)
        hash_content.pack(side="left")

        # Char Set
        hash_container = tk.Frame(self)
        hash_container.pack(side="top",  pady=5)
        label_hash_content = tk.Label(hash_container, text="Char Set:      ")
        label_hash_content.pack(side="left")
        char_set_var = tk.StringVar(hash_container)
        option = tk.OptionMenu(hash_container, char_set_var, "lower", "UPPER", "tOgGlE")
        option.configure(width=40)
        option.pack(side="left")

        # hash
        hash_container = tk.Frame(self)
        hash_container.pack(side="top", pady=5)
        label_hash_content = tk.Label(hash_container, text="Hash:             ")
        label_hash_content.pack(side="left")
        hash_text = tk.StringVar();
        hash_content = tk.Entry(hash_container, textvariable=hash_text, bg="white", width=40)
        hash_content.pack(side="left")

        label_blank1 = tk.Label(self)
        label_blank1.pack(side="top", fill="both", pady="20")

        # start button and back button
        # start_hashkittens() is the function to be called when clicking the button
        # this is an example of get input value and print it through a bind function
        start_button = tk.Button(self, text="START", width=25,
                                 command=lambda: self.start_hashkittens(hash_type_var.get(), hash_length_text.get(), char_set_var.get(), hash_text.get()))
        start_button.pack()
        back_button = tk.Button(self, text="BACK", width=25,
                           command=lambda: controller.show_frame("MainPage"))
        back_button.pack()

    def start_hashkittens(self, hash_type_var, hash_length, char_set_var, hash_text):
        print("start_hashkittens")
        #get node from DNS
        peerIP, peerTimes, peerRecordID = getPeerIP()
        #create message, send to peerIP[0]
        ni.ifaddresses('eth0')
        ip = ni.ifaddresses('eth0')[2][0]['addr']
        hashItem = hashSubmission(ip, peerIP[0], hash_type_var, hash_text, hash_length, char_set_var)
        print (peerIP[0])
        firstNode = chordNode()
        firstNode.IpAddress = peerIP[0]
        firstNode.port = 838
        submitToNetwork(firstNode, hashItem)


class JoinPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        label_blank1 = tk.Label(self)
        label_blank1.pack(side="top", fill="both", pady="3")
        label = tk.Label(self, text="Join Running Task", font=TITLE_FONT)
        label.pack(side="top", fill="x", pady=10)

        # A function to collect current tasks' statuses
        hash_list = self.getRunningHashList()

        # First row of the talbe
        topFrme = tk.Frame(self)
        label = tk.Label(topFrme, text="No.", width=4)
        label.pack(side="left", fill="x", expand=True)
        label = tk.Label(topFrme, text="Hash", width=39)
        label.pack(side="left", fill="x", expand=True)
        label = tk.Label(topFrme, text="Status", width=6)
        label.pack(side="left")
        label = tk.Label(topFrme, text="", width=4)
        label.pack(side="left", expand=True)
        topFrme.pack()

        # generate task list
        count = 0
        for hash_task in hash_list:

            hash = hash_task[0]
            status = hash_task[1]

            topFrme = tk.Frame(self)
            label = tk.Label(topFrme, text=count, width=4)
            label.pack(side="left", fill="x", expand=True)
            label = tk.Label(topFrme, text=hash, width = 40)
            label.pack(side="left", fill="x", expand=True)
            label = tk.Label(topFrme, width=4, background = self.getStatusColor(status))
            label.pack(side='left')
            if(status == 0) :
                button = tk.Button(topFrme, text='Join', width=5, command=lambda: self.joinNetwork())
                button.pack(side="left", expand=True)
            else:
                button = tk.Button(topFrme, text='Wait', width=5)
                button.pack(side="left", expand=True)
            topFrme.pack(fill='x')
            count += 1

        # back button
        label_blank1 = tk.Label(self)
        label_blank1.pack(side="top", fill="both", pady="80")
        button = tk.Button(self, text="BACK", width = 25,
                           command=lambda: controller.show_frame("MainPage"))
        button.pack()

    def joinNetwork(self):
        #trying to join network; do bootstrapping things
        peerIP, peerTimes, peerRecordID = getPeerIP()
        print ("in here")
        if len(peerIP) > 5:
          removeOldestIPEntry()
        postHostIP()

        #test code ONLY -- hardcoded IP address !! --
        #assuming call back from DNS gets back 192.168.208.172
        params = ["-p 838"]#-l 192.168.208.173"]
        connectThread = Thread(target=mainChord, args=(params))
        connectThread.daemon = False
        connectThread.start()

    def getStatusColor(self, status):
        if status == 0:
            return "green" # running
        if status == 1:
            return "grey" # paused
        if status == 2:
            return "red" # failure

    # todo: this function should be refactored in other class
    # in each element in hash_list
    # the first value is the content of hash
    # the second value is the current status of the task
    def getRunningHashList(self):
        hash_list = []
        hash_list.append(["abcdefghijklmn",0])
        hash_list.append(["opqrstuvkkkwxyz",1])
        hash_list.append(["ABCDEFGHIJKLMNOPQRSTUVWXYZ",2])
        hash_list.append(["OPQRSTUVWXYZ",0])
        return hash_list


class ResultPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        label_blank1 = tk.Label(self)
        label_blank1.pack(side="top", fill="both", pady="3")
        label = tk.Label(self, text="Crack Result", font=TITLE_FONT)
        label.pack(side="top", fill="x", pady=10)

        # todo: need to collect result from else where
        # todo: should trigger result page after the task is done
        hash = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        hash_result = "hashkitten"

        topFrame = tk.Frame(self)
        label = tk.Label(topFrame, text="input:", font=("Helvetica", 15, "bold"))
        label.pack(side='left')
        label = tk.Label(topFrame, text=hash)
        label.pack(side='left')
        topFrame.pack(side='top')

        topFrame = tk.Frame(self)
        label = tk.Label(topFrame, text="result:", font=("Helvetica", 15, "bold"))
        label.pack(side='left')
        label = tk.Label(topFrame, text=hash_result)
        label.pack(side='left')
        topFrame.pack(side='top')

        label_blank1 = tk.Label(self)
        label_blank1.pack(side="top", fill="both", pady="80")
        button = tk.Button(self, text="Back", width=25,
                           command=lambda: controller.show_frame("MainPage"))
        button.pack()


if __name__ == "__main__":
    app = SampleApp()
    app.mainloop()
