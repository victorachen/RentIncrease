import csv

path = r'C:\Users\Lenovo\PycharmProjects\rentincrease\venv\rentroll.csv'
file = open(path)
reader = csv.reader(file)
data = list(reader)
# print(data)

#given a string, return whether it is a tenant
def istenant(x):
    if len(x)>3:
        return True
#given a string, return whether it is one of our props
def isprop(x):
    if len(x)>15:
        return True

prop = 'no prop'
for r in data:
    if isprop(r[0]):
        prop = r[0]
    if istenant(r[3]):
        print(r[3]+ "--"+prop)
        
    #if A longer than 5 chars: prop = row A
    #if isTenant: write(row I) = property
