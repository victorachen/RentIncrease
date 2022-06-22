#work on renaming (line 142) for any of this to work!!
#to do: incorporate tenant owned homes
#to do: make this automatic on gmail (2 rent increase dates per year - automatically send the email)

import csv, datetime, ezgmail, os
from datetime import date, datetime
from csv import writer
os.chdir(r'C:\Users\Lenovo\PycharmProjects\rentincrease')
ezgmail.init()

#code you put in the beginning? (I suck at this)
def starter():
    rentincreasedate = '8/1/2022'
    path = r'C:\Users\Lenovo\PycharmProjects\rentincrease\venv\rentroll.csv'
    file = open(path)
    reader = csv.reader(file)
    data = list(reader)
    proplist = ['Holiday', 'Mt Vista', 'Westwind', 'Wilson Gardens', 'Crestview', \
         'Hitching Post', 'Patrician', 'Wishing Well', 'SFH']

#given a property (string), abbreviate it (or group it into broader category [like 'SFH'])
def abbr_prop(longpropname):
    SFH_list = ['Chestnut','Elm','12398 4th','12993 2nd','Reedywoods','North Grove',\
                'Massachusetts','Michigan','906 N 4th','Indian School','Cottonwood']
    for i in SFH_list:
        if i in longpropname:
            return 'SFH'
    for i in proplist:
        if i in longpropname:
            return i
    return 'No prop found'

#given a list, return whether (that row) is a tenant
def istenant(r):
    if len(r)<4:
        return False
    if len(r[3])>3 and r[4]=='Current':
        return True
#given a list, return whether (that row) is one of our props
def isprop(r):
    if len(r)<1:
        return False
    if len(r[0])>15:
        return True

#given a list, return whether (that row) is a POH tenant
def isPOH(r):
    rent = int(r[7].partition('.')[0].replace(',',''))
    if rent>500:
        return True
    else:
        return False

def days_between(currentrentincrease, lastrentincrease):
    currentrentincrease = datetime.strptime(currentrentincrease,"%m/%d/%Y")
    lastrentincrease = datetime.strptime(lastrentincrease, "%m/%d/%Y")
    return abs((currentrentincrease - lastrentincrease).days)

def timesincelastinc(r):
    timediff = ''
    if len(r[6])>1:
        return days_between(rentincreasedate,r[6])
    #if there is no recorded last rent increase, then use the move-in date
    return days_between(rentincreasedate,r[5])

#given a list, return whether (that row) is Eligible for rent increase
def isEligible(r):
    if timesincelastinc(r)>=334:
        return 'Is Eligible'
    return ''

#Holy fuck, have to rewrite alter
def alter(data):
    prop = 'no prop'
    for r in data:
        if isprop(r):
            prop = r[0]
        if istenant(r):
            # populate column I
            r.append(abbr_prop(prop))
            # populate column J
            if isPOH(r):
                r.append('POH')
            # populate column K
                r.append(timesincelastinc(r))
                r.append(isEligible(r))
            else:
                r.append('Tenant Owned')
    return data

#Helper function: loop thru data set to create new csv --> export new csv to --> output_path
def NewCsv(data,path):
    output = open(path,'w',newline='')
    writer = csv.writer(output)
    for r in data:
        writer.writerow(r)
    output.close()

#clear any given CSV
def clearCSV(path):
    filename = path
    # opening the file with w+ mode truncates the file
    f = open(filename, "w+")
    f.close()

#organize data, to make a little easier to read
def organize(data):
    #first, clear the old junk from CSV file
    path = r'C:\Users\Lenovo\PycharmProjects\rentincrease\venv\organized_output.csv'
    clearCSV(path)

    for p in proplist:
        append_list_as_row(path,[p])
        for r in data:
            if istenant(r) and isPOH(r) and isEligible(r) == "Is Eligible" and r[8] in p:
                append_list_as_row(path,r)
    return None


def append_list_as_row(file_name, list_of_elem):
    # Open file in append mode
    with open(file_name, 'a+', newline='') as write_obj:
        # Create a writer object from csv module
        csv_writer = writer(write_obj)
        # Add contents of list as last row in the csv file
        csv_writer.writerow(list_of_elem)

#On June 1st, send an email attachment with the csv file
def sendemail():
    output = r'C:\Users\Lenovo\PycharmProjects\rentincrease\venv\output.csv'
    organized_output = r'C:\Users\Lenovo\PycharmProjects\rentincrease\venv\organized_output.csv'
    ezgmail.send('vchen2120@gmail.com','6/20 getting started','',[output,organized_output])

#scrape victoreceipts@gmail.com for AppFolio's daily automated email
def DownloadRentRoll():
    resultsThreads = ezgmail.search('Automate Rent Increase')
    mostrecentemail = resultsThreads[0]

    #Download the csv into local directory
    downloadfolder = r'C:\Users\Lenovo\PycharmProjects\rentincrease\venv'
    mostrecentemail.messages[0].downloadAllAttachments(downloadFolder=downloadfolder)
    #Name the most recently downloaded rent roll (what you did just above) --> "rentroll.csv"
    today = str(date.today()).replace('-','')
    oldname = r'C:\Users\Lenovo\PycharmProjects\rentincrease\venv\rent_roll-'+today+'.csv'
    newname = r'C:\Users\Lenovo\PycharmProjects\rentincrease\venv\rentroll.csv'
    os.rename(oldname,newname)

#Before we start anything, let's delete all previous files in local directory named "rentroll.csv"
os.remove(r'C:\Users\Lenovo\PycharmProjects\rentincrease\venv\rentroll.csv')
#Then, let's download a fresh rentroll from Appfolio
DownloadRentRoll()

#Now, we can start (the rest of) our code
#------------------------------------------------------------------------------------------
starter()
# Create the output csv
altered_data = alter(data)
output_path = r'C:\Users\Lenovo\PycharmProjects\rentincrease\venv\output.csv'
NewCsv(altered_data, output_path)

# Create the organized_output csv
organize(altered_data)

#send the email to all prop managers
# sendemail()
