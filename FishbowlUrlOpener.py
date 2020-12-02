from tkinter import *
import tkinter.messagebox as messagebox
import tkinter.ttk as ttk
import mysql.connector, logging, configparser, os, os.path, subprocess, utilitys, configHelper, customExceptions, urllib.parse
import appIcon


root = Tk()

#========================================VARIABLES========================================
WINDOW_ICON = PhotoImage(data=appIcon.ICON)

PROGRAM_VERSION = "1.0.0"
PROGRAM_NAME_STRING = "FishbowlUrlOpener"
PROGRAM_NAME = utilitys.amendSpacesToString(PROGRAM_NAME_STRING)
PROGRAM_TITLE = f"{PROGRAM_NAME} ({PROGRAM_VERSION})"
SCREEN_WIDTH, SCREEN_HEIGHT = root.winfo_screenwidth(), root.winfo_screenheight()


try:
    LOG_FILE_NAME = configHelper.LOG_FILE_NAME
    COFIG_FILE_NAME = configHelper.COFIG_FILE_NAME
    CONNECTION_PARMS = configHelper.readConfigSection(COFIG_FILE_NAME, "FishbowlDatabase")
    LOG_FILE_SIZE_LIMIT = int(configHelper.readConfigSection(COFIG_FILE_NAME, "Logging")['logfilesizelimit'])
except:
    messagebox.showerror("Error", "An unknow error occurred when reading .ini files. Try deleting all .ini files where this program .exe is located. Then try again.")
    exit()

rootWidth = 375
rootHeight = 150
x = (SCREEN_WIDTH/2) - (rootWidth/2)
y = (SCREEN_HEIGHT/2) - (rootHeight/2)
root.geometry("%dx%d+%d+%d" % (rootWidth, rootHeight, x, y))
root.resizable(0, 0)
root.title(PROGRAM_TITLE)
root.tk.call('wm', 'iconphoto', root._w, WINDOW_ICON)

if not os.path.isfile(LOG_FILE_NAME):
    with open(LOG_FILE_NAME, 'w') as logFile:
        logFile.write('')
    logFile.close()


# Check log file size
currentLogFileSize = utilitys.getFileSize(LOG_FILE_NAME)
if currentLogFileSize > LOG_FILE_SIZE_LIMIT:
    with open(LOG_FILE_NAME, 'w') as logFile:
        logFile.write(f"Log file exceeded size limit of {str(LOG_FILE_SIZE_LIMIT)}kb. {LOG_FILE_NAME} was cleared.\n\n")
    logFile.close()

try:
    LogVerbosityValue = configHelper.readConfigSection(COFIG_FILE_NAME, "Logging")['logverbosity']
except (customExceptions.NoSectionError, KeyError) as err:
    LogVerbosityValue = 'WARNING'
#Create and configure logger
logging.basicConfig(filename=LOG_FILE_NAME, format='%(asctime)s - %(levelname)s: %(message)s', filemode='a',
                        datefmt='%m/%d/%Y %I:%M:%S %p')
#Create a logging object
logger=logging.getLogger()
#Setting the threshold of logger
logger.setLevel(LogVerbosityValue)

logger.debug(f"[CONFIG] Contents of {COFIG_FILE_NAME} \n\t{configHelper.readConfigFile(COFIG_FILE_NAME)}")
logger.info(f"[CONFIG] Logging level set to {LogVerbosityValue}")
logger.info(f"[VERSION] Current program version: {PROGRAM_VERSION}")


#========================================METHODS========================================
def Database():
    try:
        db = mysql.connector.connect(**CONNECTION_PARMS)
    except mysql.connector.Error as err:
        info = str("Something went wrong in Database: {}".format(err))
        logger.critical("There was an error when atempting to connect to the database with the parms below.")
        logger.critical(f"Parms Used \n\t{CONNECTION_PARMS}")
        logger.critical(f"Error: {err}")
        messagebox.showerror("MySQL", info)
    return db


def GetCursor():
    global conn
    try:
        conn.ping(reconnect=True, attempts=5, delay=3)
    except:
        conn = Database()
    return conn.cursor()


def Exit():
    # result = messagebox.askquestion('Time Tracking', 'Are you sure you want to exit?', icon="warning")
    result = 'yes'
    if result == 'yes':
        root.destroy()
        try:
            conn.close()
        except:
            pass
        exit()


def SaveSettings():
    logger.info("[CONFIG] Saving new settings.")
    for section in configData:
        for key in configData[section]:
            configHelper.updateConfigSection(COFIG_FILE_NAME, section, key, entreBoxList[key].get())
            logger.debug(f"[CONFIG] Updating Section: [{section}] Key: [{key}] Changing value to [{entreBoxList[key].get()}]")

    settings.destroy()
    logger.info("[CONFIG] New settings saved.")
    if messagebox.askquestion(PROGRAM_NAME, "Settings Saved. For the new settings to take effect close then reopen the program.\n\nWould you like to close now?") == 'yes':
        Exit()
    return


def ShowConfigSettings():
    global settings
    settings = Toplevel(root)
    settings.title("Settings")
    #settings.resizable(False, False)
    settings.tk.call('wm', 'iconphoto', settings._w, WINDOW_ICON)

    global configData
    configData = configHelper.readConfigFile(COFIG_FILE_NAME)
    rowNum = 0
    global entreBoxList
    entreBoxList = {}
    for section in configData:
        Label(settings, text=section, font='bold').grid(row=rowNum, column=0)
        rowNum += 1
        for key in configData[section]:
            Label(settings, text=key).grid(row=rowNum, column=0)
            entryBox = Entry(settings, width=25)
            entryBox.grid(row=rowNum, column=1, padx=5, pady=3)
            entryBox.insert(0, configData[section][key])
            entreBoxList[key] = entryBox
            rowNum += 1
        Label(settings, text='').grid(row=rowNum, column=0)
        rowNum += 1
    saveButton = Button(settings, text="Save Settings", command=SaveSettings)
    saveButton.grid(row=rowNum, column=0, columnspan=2, pady=5)


def OpenFile(fullFilePath):
    os.startfile('"' + os.path.abspath(fullFilePath)+ '"')
    partnumberEntry.delete(0, END)
    return


def decodeUrlString(encodedStr):
    logger.debug(f"Decoding URL string {encodedStr}")
    return urllib.parse.unquote(encodedStr)


def getUrlType(decodedUrlString):
    logger.debug(f"Parsing decoded URL string {decodedUrlString}")
    urlType, urlString = decodedUrlString.split('//', 1)
    logger.debug(f"URL Type: {urlType}  URL String: {urlString}")
    return {'Type': urlType.rstrip(':'), 'String': urlString.lstrip('/')}



def GetFile(event=None):
    partNumberValue = partnumberEntry.get().upper()
    logger.debug(f"Part number entered = {partNumberValue}")
    if len(partNumberValue) == 0:
        info = "Part number can not be blank."
        logger.error(info)
        messagebox.showerror(PROGRAM_NAME, info)
        return

    cursor = GetCursor()
    partDataQuery = """SELECT part.num, part.description, part.url FROM part WHERE part.num = %s"""
    logger.debug(f"[QUERY RUN] Query: {partDataQuery} \n\tParms: {partNumberValue}")
    cursor.execute(partDataQuery, (partNumberValue, ))
    partData = cursor.fetchall()
    cursor.close()
    logger.debug(f"[QUERY DATA] {partData}")

    if not partData:
        info = f"Part Number: {partNumberValue} could not be found. Please double check and try again."
        logger.warning(info)
        messagebox.showwarning(PROGRAM_NAME, info)
        return

    urlRawString = partData[0][2]
    if urlRawString == '':
        info = f"Part Number: {partNumberValue} does not have an associated file to open. Please get with engineering to add a file to this part."
        logger.warning(info)
        messagebox.showerror(PROGRAM_NAME, info)
        return

    decodedData = getUrlType(decodeUrlString(urlRawString))

    if decodedData['Type'] != 'file':
        info = f"Data type: {decodedData['Type']} is not supported."
        logger.error(info)
        messagebox.showerror(PROGRAM_NAME, info)
        return

    logger.debug(f"[OPEN FILE] Opening file from path {decodedData['String']}")
    OpenFile(decodedData['String'])
    return


partNumberLabel = Label(root, text="Part Number:", font=("Helvetica", 14, 'bold'))
partNumberLabel.grid(row=0, column=0, padx=5, pady=5)

partnumberEntry = Entry(root, font=("Helvetica", 14, 'bold'))
partnumberEntry.grid(row=0, column=1, padx=5, pady=5)
partnumberEntry.focus()
partnumberEntry.bind('<Return>', GetFile)

submitButton = Button(root, text="Find Print", command=GetFile, font=("Helvetica", 14, 'bold'))
submitButton.grid(row=1, column=0, columnspan=2, padx=5, pady=5)
submitButton.bind('<Return>', GetFile)

#========================================MENUBAR WIDGETS==================================
menubar = Menu(root)
root.config(menu=menubar)

filemenu = Menu(menubar, tearoff=0)
menubar.add_cascade(label="File", menu=filemenu)

filemenu.add_command(label="Settings", command=ShowConfigSettings)
filemenu.add_command(label="Exit", command=Exit)

#========================================INITIALIZATION===================================
root.protocol("WM_DELETE_WINDOW", Exit)
logger.info(f"[MYSQL] Current database connection parms \n\t{CONNECTION_PARMS}")

if __name__ == '__main__':
    root.mainloop()