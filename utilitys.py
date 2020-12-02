import os.path
import os
import re

#TODO: Add doc strings.
def getFileSize(fileName):
    st = os.stat(os.path.abspath(fileName))
    return st.st_size


def amendSpacesToString(inputString):
    words = re.findall('[A-Z][a-z]*', inputString)
    stringList = []
    for word in words:
        stringList.append(word)
    return ' '.join(stringList)