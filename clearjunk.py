#we have to create this second python file, because can't clear the junk
#within the main.py file.... don't know why
import os

def DeleteEverythingInFolder(path):
    os.chdir(path)
    mydir = path
    filelist = [f for f in os.listdir(mydir)]
    for f in filelist:
        os.remove(os.path.join(mydir, f))

path = 'C:\\Users\\19097\\PycharmProjects\\rentincrease\\venv\\FillPDFs\\indiv_notices'

DeleteEverythingInFolder(path)
