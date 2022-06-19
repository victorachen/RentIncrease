#to do: line 79 -- organize function
#to do: (2) mapping SFH --> diff names in output.csv file

import csv, datetime
from datetime import date, datetime
from csv import writer

rentincreasedate = '8/1/2022'
path = r'C:\Users\Lenovo\PycharmProjects\rentincrease\venv\rentroll.csv'
file = open(path)
reader = csv.reader(file)
data = list(reader)
# print(data)

#given a property (string), abbreviate it (or group it into broader category [like 'SFH'])
def abbr_prop(longpropname):
    proplist = ['Holiday', 'Mt Vista', 'Westwind', 'Wilson Gardens', 'Crestview', \
     'Hitching Post', 'SFH', 'Patrician', 'Wishing Well']
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
    if len(r[3])>3 and r[4]=='Current':
        return True
#given a list, return whether (that row) is one of our props
def isprop(r):
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
    if timesincelastinc(r)>=365:
        return 'Eligible'
    return ''

#given a csv data set (list), alter the data set according to how we want to alter the csv
def alter(data):
    prop = 'no prop'
    for r in data:

        if isprop(r):
            prop = r[0]
        if istenant(r):
            # populate column I
            r[8] = prop
            # populate column J
            if isPOH(r):
                r[9] = 'POH'
                # populate column K
                r[10] = timesincelastinc(r)
                r[11] = isEligible(r)
            else:
                r[9] = 'Tenant Owned'

    return data

#Helper function: loop thru data set to create new csv --> export new csv to --> output_path
def NewCsv(data,path):
    output = open(path,'w',newline='')
    writer = csv.writer(output)
    for r in data:
        writer.writerow(r)
    output.close()

#organize data, to make a little easier to read
def organize(data):
    print ('lorem ipsum: still working')

# Create the output csv
output_path = r'C:\Users\Lenovo\PycharmProjects\rentincrease\venv\output.csv'
NewCsv(alter(data), output_path)

#Lastly, Create the organized_output.csv
# organized_path = r'C:\Users\Lenovo\PycharmProjects\rentincrease\venv\organized_output.csv'
# NewCsv(organize(alter(data)), organized_path)

def append_list_as_row(file_name, list_of_elem):
        # Open file in append mode
        with open(file_name, 'a+', newline='') as write_obj:
            # Create a writer object from csv module
            csv_writer = writer(write_obj)
            # Add contents of list as last row in the csv file
            csv_writer.writerow(list_of_elem)

file_name = r'C:\Users\Lenovo\PycharmProjects\rentincrease\venv\test.csv'
list = ['a','b','c','d','e','f']
append_list_as_row(file_name,list)
