import cv2, webbrowser, numpy as np, argparse, time, glob, os, sys, subprocess, pandas, random, Update_Model, math, ctypes
#Define variables and load classifier
new=2
camnumber = 0
video_capture = cv2.VideoCapture()
facecascade = cv2.CascadeClassifier("C:/Users/lenovo/AppData/Roaming/Python/Python37/site-packages/cv2/data/haarcascade_frontalface_default.xml")
fishface = cv2.face.FisherFaceRecognizer_create()
try:
    fishface.read("trained_emoclassifier.xml")
except:
    print("no trained xml file found, please run program with --update flag first")
parser = argparse.ArgumentParser(description="Options for the emotion-based music player")
parser.add_argument("--update", help="Call to grab new images and update the model accordingly", action="store_true")
parser.add_argument("--retrain", help="Call to re-train the the model based on all images in training folders", action="store_true") #Add --update argument
#parser.add_argument("--wallpaper", help="Call to run the program in wallpaper change mode.", type=int) #Add --update argument
args = parser.parse_args()
facedict = {}
actions = {}
youtubelinks = {}
wp={}
emotions = ["angry", "happy", "sad", "neutral"]
df = pandas.read_excel("EmotionLinks.xlsx") #open Excel file
df1 = pandas.read_excel("YoutubeLinks.xlsx")
df2 = pandas.read_excel("ImageLinks.xlsx")
youtubelinks["angry"] = [x for x in df1.angry.dropna()] #We need de dropna() when columns are uneven in length, which creates NaN values at missing places. The OS won't know what to do with these if we try to open them.
youtubelinks["happy"] = [x for x in df1.happy.dropna()]
youtubelinks["sad"] = [x for x in df1.sad.dropna()]
youtubelinks["neutral"] = [x for x in df1.neutral.dropna()]
actions["angry"] = [x for x in df.angry.dropna()] #We need de dropna() when columns are uneven in length, which creates NaN values at missing places. The OS won't know what to do with these if we try to open them.
actions["happy"] = [x for x in df.happy.dropna()]
actions["sad"] = [x for x in df.sad.dropna()]
actions["neutral"] = [x for x in df.neutral.dropna()]
wp["angry"] = [x for x in df2.angry.dropna()] #We need de dropna() when columns are uneven in length, which creates NaN values at missing places. The OS won't know what to do with these if we try to open them.
wp["happy"] = [x for x in df2.happy.dropna()]
wp["sad"] = [x for x in df2.sad.dropna()]
wp["neutral"] = [x for x in df2.neutral.dropna()]
#print ("HIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII")
#print (actions["angry"])

def open_diary():
    filename = "C:/Users/lenovo/Desktop/OST/diary_entry.txt"
    if sys.platform == "win32":
        print ("True")
        os.startfile(filename)
    else:
        opener ="open" if sys.platform == "darwin" else "xdg-open"
        print ("opn2")
        subprocess.call([opener, filename])
    

    
def open_song(filename): #Open the file, credit to user4815162342, on the stackoverflow link in the text above
    if sys.platform == "win32":
        print ("True")
        os.startfile(filename)
    else:
        opener ="open" if sys.platform == "darwin" else "xdg-open"
        print ("opn2")
        subprocess.call([opener, filename])

def open_youtube(url):
    webbrowser.open(url, new=new)
    
        
def crop_face(clahe_image, face):
    for (x, y, w, h) in face:
        faceslice = clahe_image[y:y+h, x:x+w]
        faceslice = cv2.resize(faceslice, (350, 350))
    facedict["face%s" %(len(facedict)+1)] = faceslice
    return faceslice

def update_model(emotions):
    print("Model update mode active")
    check_folders(emotions)
    for i in range(0, len(emotions)):
        save_face(emotions[i])
    print("collected images, looking good! Now updating model...")
    Update_Model.update(emotions)
    print("Done!")
    
def check_folders(emotions):
    for x in emotions:
        if os.path.exists("dataset\\%s" %x):
            pass
        else:
            os.makedirs("dataset\\%s" %x)
            
def save_face(emotion):
    print("\n\nplease look " + emotion + ". Press enter when you're ready to have your pictures taken")
    #raw_input() #Wait until enter is pressed with the raw_input() method
    video_capture.open(camnumber)
    while len(facedict.keys()) < 16:
        detect_face()
    video_capture.release()
    for x in facedict.keys():
        cv2.imwrite("dataset\\%s\\%s.jpg" %(emotion, len(glob.glob("dataset\\%s\\*" %emotion))), facedict[x])
    facedict.clear()
    
def recognize_emotion():
    predictions = []
    confidence = []
    for x in facedict.keys():
        pred, conf = fishface.predict(facedict[x])
        cv2.imwrite("images\\%s.jpg" %x, facedict[x])
        predictions.append(pred)
        confidence.append(conf)
    recognized_emotion = emotions[max(set(predictions), key=predictions.count)]
    print("I think you're %s" %recognized_emotion)
    return recognized_emotion

def grab_webcamframe():
    ret, frame = video_capture.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    clahe_image = clahe.apply(gray)
    return clahe_image

def detect_face():
    clahe_image = grab_webcamframe()
    face = facecascade.detectMultiScale(clahe_image, scaleFactor=1.1, minNeighbors=15, minSize=(10, 10), flags=cv2.CASCADE_SCALE_IMAGE)
    if len(face) == 1:
        faceslice = crop_face(clahe_image, face)
        return faceslice
    else:
        print("no/multiple faces detected, passing over frame")
        
def run_detection():
    while len(facedict) != 10:
        detect_face()
    recognized_emotion = recognize_emotion()
    return recognized_emotion

def wallpaper_timer(seconds):
    video_capture.release()
    time.sleep(int(seconds))
    video_capture.open(camnumber)
    facedict.clear()
    
def change_wallpaper(emotion):
    files = glob.glob("wallpapers\\%s\\*.bmp" %emotion)
    print ("kjkhhhhhhhhhhhhh")
    current_dir = os.getcwd()
    random.shuffle(files)
    file = "%s\%s" %(current_dir, files[0])
    setWallpaperWithCtypes(file)
    
def setWallpaperWithCtypes(path): #Taken from http://www.blog.pythonlibrary.org/2014/10/22/pywin32-how-to-set-desktop-background/
    cs = path
    SPI_SETDESKWALLPAPER = 20
    print (cs)
    ok = ctypes.windll.user32.SystemParametersInfoA(SPI_SETDESKWALLPAPER, 0, cs, 0)

actionlist=[]
youtubeactionlist=[]
wpactionlist=[]
if args.update:
    update_model(emotions)
    exit()
elif args.retrain:
    Update_Model.update(emotions)
    exit()
        
else:
    video_capture.open(camnumber)
    recognized_emotion = run_detection()
    actionlist = [x for x in actions[recognized_emotion]]#get list of actions/files for detected emotion
    youtubeactionlist = [x for x in youtubelinks[recognized_emotion]]
    wpactionlist=[x for x in wp[recognized_emotion]]
    print (actionlist)
    random.shuffle(actionlist)
    random.shuffle(youtubeactionlist)#Randomly shuffle the list
    


from tkinter import *
 
window = Tk()
 
window.title("Pacify yourself")
 
window.geometry('500x500')
 
lbl = Label(window, text="Choose any of the options -")
 
lbl.grid(column=0, row=0)
 
def play_music():
    print(actionlist)
    open_song(actionlist[random.randrange(0,5)])
    random.shuffle(actionlist)
    

def watch_video():
    open_youtube(youtubeactionlist[random.randrange(0,5)])
    random.shuffle(youtubeactionlist)
    
def change_wp():
    x = wpactionlist[random.randrange(0,5)]

    change_wallpaper(recognized_emotion)
    setWallpaperWithCtypes(x)
    print (type(x))
    print (x)
    random.shuffle(wpactionlist)
    
def diary():
    open_diary()
   
    
def chatbot():
    url= 'https://bot.dialogflow.com/ade07d89-4bf0-422d-ae99-86816ef98541'
    webbrowser.open(url, new=new)
 
btn1 = Button(window, text="Listen to some music", command=play_music)
btn2 = Button(window, text="Watch Videos", command=watch_video)
btn5 = Button(window, text="Change Wallpaper", command=change_wp)
btn4 = Button(window, text="Chat with the bot", command=chatbot)
btn3 = Button(window, text="Make a diary entry", command=diary)
 
btn1.grid(column=5, row=3)
btn2.grid(column=5, row=5)
btn3.grid(column=5, row=7)
btn4.grid(column=5, row=9)
btn5.grid(column=5, row=11)
 
window.mainloop()


video_capture.release()
cv2.destroyAllWindows()
