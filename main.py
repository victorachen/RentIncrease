#adjust isEligible function (calls lastincreasedate, which takes in 2 arguments now)
#update your email body
#send on the 1st of every month
#to do: incorporate tenant owned homes
#to do: make this automatic on gmail (2 rent increase dates per year - automatically send the email)

import csv, datetime, ezgmail, os
import os.path
from datetime import date, datetime
from csv import writer
os.chdir(r'C:\Users\Lenovo\PycharmProjects\rentincrease')
ezgmail.init()

#return the date 3 months from now (copied pasted from stackoverflow)
def Xmonthsfromnow(x):
    D = {1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun', 7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct',
                 11: 'Nov', 12: 'Dec'}
    today = date.today()
    day = today.day
    month = today.month
    year = today.year
    inc = x
    month = (month + inc - 1) % 12 + 1
    year = year + (month + inc - 1) // 12
    #return the end result as a string, so we can compare with getstrtoday()
    combined = str(month)+'/'+str(day)+'/'+str(year)
    return combined

# rentincreasedate = Xmonthsfromnow(2)
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

def timesincelastinc(r,tenant_type):
    if tenant_type == 'POH':
        rentincreasedate = Xmonthsfromnow(2)
    if tenant_type == 'TOH':
        rentincreasedate = Xmonthsfromnow(4)
    timediff = ''
    if len(r[6])>1:
        return days_between(rentincreasedate,r[6])
    #if there is no recorded last rent increase, then use the move-in date
    return days_between(rentincreasedate,r[5])

#given a list, return whether (that row) is Eligible for rent increase
def isEligible(r):
    if timesincelastinc(r,'POH')>=334:
        return 'Is Eligible'
    return ''

def alterPOH(data):
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
                r.append(timesincelastinc(r,'POH'))
                r.append(isEligible(r))
            else:
                r.append('Tenant Owned')
    return data

#copied pasta'd from above (fingers crossed it works)
def alterTOH(data):
    prop = 'no prop'
    for r in data:
        if isprop(r):
            prop = r[0]
        if istenant(r):
            # populate column I
            r.append(abbr_prop(prop))
            # populate column J
            if not isPOH(r):
                r.append('Tenant Owned')
                # populate column K
                r.append(timesincelastinc(r,'TOH'))
                r.append(isEligible(r))
            else:
                r.append('POH')
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

#create CSV for eligible POH residents
def eligiblePOH(data):
    #first, clear the old junk from CSV file
    path = r'C:\Users\Lenovo\PycharmProjects\rentincrease\venv\eligiblePOH.csv'
    clearCSV(path)

    # title each column
    titles = ['Unit #', '', 'Bd/Ba', 'Tenant', 'Status', 'Move-in', 'Last Increase', '$ Rent', 'Property',
              'Type', 'Days Since Last Increase', 'Eligibility']
    append_list_as_row(path, titles)
    append_list_as_row(path, [])

    for p in proplist:
        append_list_as_row(path,[p])
        for r in data:
            if istenant(r) and isPOH(r) and isEligible(r) == "Is Eligible" and r[8] in p:
                append_list_as_row(path,r)
    return None

#copied pasta from above
def eligibleTOH(data):
    #first, clear the old junk from CSV file
    path = r'C:\Users\Lenovo\PycharmProjects\rentincrease\venv\eligibleTOH.csv'
    clearCSV(path)

    #title each column
    titles=['Unit #','','Bd/Ba','Tenant','Status','Move-in','Last Increase','$ Rent','Property',
            'Type','Days Since Last Increase','Eligibility']
    append_list_as_row(path,titles)
    append_list_as_row(path,[])

    for p in proplist:
        append_list_as_row(path,[p])
        for r in data:
            if istenant(r) and not isPOH(r) and isEligible(r) == "Is Eligible" and r[8] in p:
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
    POHoutput = r'C:\Users\Lenovo\PycharmProjects\rentincrease\venv\POHoutput.csv'
    TOHoutput = r'C:\Users\Lenovo\PycharmProjects\rentincrease\venv\TOHoutput.csv'
    eligiblePOH = r'C:\Users\Lenovo\PycharmProjects\rentincrease\venv\eligiblePOH.csv'
    eligibleTOH = r'C:\Users\Lenovo\PycharmProjects\rentincrease\venv\eligibleTOH.csv'
    emailtitle = 'POH Residents Eligible for Rent Increase On '+Xmonthsfromnow(2)
    emailbody = '''This is an automated email detailing those POH tenants who are eligible for rent increase 2 months from now ('''+ Xmonthsfromnow(2)+'''). \n 
    TOH csv files reflect those tenants eligible for rent 4 months from now'''

    ezgmail.send('vchen2120@gmail.com',emailtitle,emailbody,[POHoutput,TOHoutput,eligiblePOH,eligibleTOH])


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

#get data from Rent Roll
def GetData():
    path = r'C:\Users\Lenovo\PycharmProjects\rentincrease\venv\rentroll.csv'
    file = open(path)
    reader = csv.reader(file)
    data = list(reader)
    return data

#Before we start anything, let's delete all previous files in local directory named "rentroll.csv"
fname = r'C:\Users\Lenovo\PycharmProjects\rentincrease\venv\rentroll.csv'
if os.path.isfile(fname):
    os.remove(fname)
#Then, let's download a fresh rentroll from Appfolio
DownloadRentRoll()

# Create POHoutput.csv
POH_data = alterPOH(GetData())
output_path = r'C:\Users\Lenovo\PycharmProjects\rentincrease\venv\POHoutput.csv'
NewCsv(POH_data, output_path)

#Create TOHoutput.csv
TOH_data = alterTOH(GetData())
output_path = r'C:\Users\Lenovo\PycharmProjects\rentincrease\venv\TOHoutput.csv'
NewCsv(TOH_data, output_path)

# Create eligiblePOH.csv
eligiblePOH(POH_data)

#create eligibleTOH.csv
eligibleTOH(TOH_data)

#send the email to all prop managers
sendemail()