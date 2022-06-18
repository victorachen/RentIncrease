#to do: fix rentincreasedate, then work on 'iseligible' function
#if there is no "last rent increase" date, and this doesn't correspond with
#the move-in date, be sure to flag that there is something wrong with tenant
import csv, math

rentincreasedate = 'Aug 1st, 2022 '
path = r'C:\Users\Lenovo\PycharmProjects\rentincrease\venv\rentroll.csv'
file = open(path)
reader = csv.reader(file)
data = list(reader)
# print(data)

#given a list, return whether (that row) is a tenant
def istenant(r):
    if len(r[3])>3 and r[4]=='Current':
        return True
#given a list, return whether (that row) is one of our props
def isprop(r):
    if len(r[0])>15:
        return True
def isPOH(r):
    rent = int(r[7].partition('.')[0].replace(',',''))
    if rent>500:
        return True
    else:
        return False

#is tenant eligible for rent increase?
def isEligible(r):
    #case 1: if last rent increase was one yr ago, return true

    #case 2: if there is no last rent increase, when was the move-in date?
    #if move-in date is more than 1 yr, then return true

#given a csv data set (list), alter the data set according to how we want to alter the csv
def alter(data):
    prop = 'no prop'
    for r in data:
        #populate column I
        if isprop(r):
            prop = r[0]
        if istenant(r):
            r[8] = prop
            if isPOH(r):
                r[9] = 'POH'
            else:
                r[9] = 'Tenant Owned'
        #populate column J

    return data

#loop thru altered data set to create new csv
def NewCsv(data):
    path = r'C:\Users\Lenovo\PycharmProjects\rentincrease\venv\output.csv'
    output = open(path,'w',newline='')
    writer = csv.writer(output)
    for r in data:
        writer.writerow(r)
    output.close()

# print(alter(data))
NewCsv(alter(data))

    #if A longer than 5 chars: prop = row A
    #if isTenant: write(row I) = property
