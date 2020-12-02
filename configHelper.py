import customExceptions, configparser, configHelper, os, os.path
from tkinter import messagebox

def readConfigFile(cofigFileName):
    if not os.path.isfile(cofigFileName):
        raise FileExistsError("File or file path does not exist.")
    configData = {}
    config = configparser.ConfigParser()
    config.read(cofigFileName)
    for sect in config.sections():
        item = {}
        for k,v in config.items(sect):
            item[k] = v
        configData[sect] = item
    return configData


def readConfigSection(cofigFileName, section):
    config = configparser.ConfigParser()
    config.read(cofigFileName)
    sectionOptions= {}
    if config.has_section(section):
        items = config.items(section)
        for item in items:
            sectionOptions[item[0]] = item[1]
    else:
        raise customExceptions.NoSectionError('Section: [{0}] not found in Config File: [{1}]'.format(section, cofigFileName))
    return sectionOptions # Return a dictionary of the section options


def updateConfigSection(cofigFileName, section, key, value):
    config = configparser.ConfigParser()
    config.read(cofigFileName)
    config.set(section, key, value)
    with open(cofigFileName, 'w') as configfile:
        config.write(configfile)
    configfile.close()
    return

COFIG_FILE_NAME = "FishbowlUrlOpenerConfig.ini"
LOG_FILE_NAME = "FishbowlUrlOpenerLog.txt"

# Create default config file if not there
if not os.path.isfile(COFIG_FILE_NAME):
    config = configparser.ConfigParser()

    # Define sections with Key: Value pairs
    config['TFishbowlDatabase'] = {'host': '127.0.0.1',
                        'port': '3305',
                        'user': 'gone',
                        'password': 'fishing',
                        'database': 'db_name',
                        'auth_plugin': 'mysql_native_password'}

    config['Logging'] = {'LogVerbosity': 'WARNING',
                            'LogFileSizeLimit': '20000'
                            }

    with open(COFIG_FILE_NAME, 'w') as configfile:
        config.write(configfile)
    configfile.close()
try:
    LOG_VERBOSITY_VALUE = readConfigSection(COFIG_FILE_NAME, "Logging")['logverbosity']
except:
    messagebox.showerror("Error", "An unknow error occurred when reading .ini files. Try deleting all .ini files where this program .exe is located. Then try again.")
    exit()