#ready to go: test out a bunch of diff dates, then set dateinput to today()
#play around with the bolding: https://ezgmail.readthedocs.io/en/latest/
#after: write a separate script to generate PDF's of rent increase letters for Resident Owned Homes

import datetime
dateinput = datetime.date(2022,7,1)

from PyPDF2 import PdfFileWriter, PdfFileReader, PdfFileMerger
from datetime import date, datetime
today = date.today()
# print(dateinput==today)

import csv, ezgmail, os, io
import os.path
from csv import writer
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
os.chdir(r'C:\Users\Lenovo\PycharmProjects\rentincrease')
ezgmail.init()

#return the date 3 months from dateinput
def Xmonthsfromnow(x,dateinput):
    day = dateinput.day
    this_month = dateinput.month
    this_year = dateinput.year
    inc = x
    month = (this_month + inc - 1) % 12 + 1
    year = this_year + (this_month + inc - 1) // 12
    #return the end result as a string, so we can compare with getstrtoday()
    combined = str(month)+'/'+str(day)+'/'+str(year)
    return combined

#convert "2023-10-01" to string "October 2023"
def convertdate(date):
    D = {1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun',
                 7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'}
    month = date.month
    mapped_month = D[month]
    year = date.year
    combined = mapped_month + " "+ str(year)
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
        rentincreasedate = Xmonthsfromnow(2,dateinput)
    if tenant_type == 'TOH':
        rentincreasedate = Xmonthsfromnow(4,dateinput)
    timediff = ''
    if len(r[6])>1:
        return days_between(rentincreasedate,r[6])
    #if there is no recorded last rent increase, then use the move-in date
    return days_between(rentincreasedate,r[5])

#given a list, return whether (that row) is Eligible for rent increase
def isEligible(r,tenant_type):
    if timesincelastinc(r,tenant_type)>=330:
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
                r.append(isEligible(r,'POH'))
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
                r.append(isEligible(r,'TOH'))
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
    header = ['*Today is '+convertdate(dateinput)+'; below shows all POH tenants eligible for increase 90 days from now on ' + Xmonthsfromnow(2,dateinput)]
    append_list_as_row(path, header)
    append_list_as_row(path, titles)
    append_list_as_row(path, [])

    for p in proplist:
        append_list_as_row(path,[p])
        for r in data:
            if istenant(r) and isPOH(r) and isEligible(r,'POH') == "Is Eligible" and r[8] in p:
                append_list_as_row(path,r)
    return None

# Dictionary representing which months can push out Rent Increase for TOH
TOH_Dic = {'Hitching Post': 7, 'Wishing Well': 10, 'Holiday': 2, 'Mt Vista': 2, 'Crestview': 1,'Westwind':7}
#Second Dic: ex) if hitching rent increase takes place in month 7, send out notif email during month 3
TOH_Dic_90daysprior = {'Hitching Post': 3, 'Wishing Well': 6, 'Holiday': 10, 'Mt Vista': 10, 'Crestview': 9,'Westwind':3}

#helper for EligibleTOH() -- return list (eligibleTOHproplist) of props where it is time (this month) to pass out 90 days
def EligTOHlist():
    L = []
    for prop in TOH_Dic_90daysprior:
        if TOH_Dic_90daysprior[prop] == dateinput.month:
            L.append(prop)
    return L

#create CSV for eligible TOH residents
def eligibleTOH(data):
    #first, clear the old junk from CSV file
    path = r'C:\Users\Lenovo\PycharmProjects\rentincrease\venv\eligibleTOH.csv'
    clearCSV(path)

    #title each column
    titles=['Unit #','','Bd/Ba','Tenant','Status','Move-in','Last Increase','$ Rent','Property',
            'Type','Days Since Last Increase','Eligibility']
    header = ['*Today is '+convertdate(dateinput)+'; below shows all TOH tenants eligible for increase 90 days from now on' + Xmonthsfromnow(4,dateinput)]
    append_list_as_row(path, header)
    append_list_as_row(path,titles)
    append_list_as_row(path,[])

    for p in TOH_Dic:
        if p in EligTOHlist():
            append_list_as_row(path, [p])
            for r in data:
                if istenant(r) and not isPOH(r) and r[8] in p:
                    append_list_as_row(path,r)
        else:
            append_list_as_row(path, [p+': No TOH Increases For This Month!'])
    return None

def append_list_as_row(file_name, list_of_elem):
    # Open file in append mode
    with open(file_name, 'a+', newline='') as write_obj:
        # Create a writer object from csv module
        csv_writer = writer(write_obj)
        # Add contents of list as last row in the csv file
        csv_writer.writerow(list_of_elem)

#helper for emailbody()
def areanyTOHeligible4increase():
    if dateinput.month in TOH_Dic_90daysprior.values():
        return True
    return False
#helpers for emailbody()
def areanyPOHeligible4increase():
    if dateinput.month == 6 or dateinput.month == 11:
        return True
    return False


#return the text of the email body as a string
def emailbody():
    emailbody = '''<p><u>Rent increases we need to pass out this month <strong>('''+ convertdate(dateinput) + ')</strong>:<br></u></p>'

    #only pass out POH Rent Increases during beginning & middle of the year (Aug 1st [6] & Feb 1st [11])
    if areanyPOHeligible4increase():
        POHbody = '''(1) <em>POH</em>: Hitching Post, Wishing Well, Holiday, Mt Vista, Crestview, Patrician, & Westwind need 30 day notices passed out. Rent Increase Date: ''' + Xmonthsfromnow(2,dateinput)+"-- <br><em> see 'eligiblePOH.csv' for a list of POH tenants needing increases</em><br>"
    else:
        POHbody = '(1)<em> POH</em>: No increases to pass out this month!<br>'

    ifTOHno = '\n (2) <em>TOH</em>:  No increases to pass out this month!<br>'
    ifTOHyes = '''90 day notices passed out this month -- Increase To Take Effect <strong>''' + Xmonthsfromnow(4, dateinput) + '''</strong><br>
<em>(See 'eligibleTOH.csv' for a list of TOH tenants needing increases)</em><br>'''
    TOHbody = '(2)<em> TOH<em>: '

    count = 0
    for prop in TOH_Dic_90daysprior:
        if dateinput.month == TOH_Dic_90daysprior[prop]:
            TOHbody = TOHbody + '<strong>'+ prop + '</strong>'+', '
            count+=1
    if areanyTOHeligible4increase():
        #gotta make sure this is grammatically correct, ya know
        if count > 1:
            TOHbody = TOHbody + 'need '+ ifTOHyes
        if count <=1:
            TOHbody = TOHbody + 'needs '+ifTOHyes
    else:
        TOHbody = ifTOHno

    Tailbody = '''
<p><u><strong>Notes: </strong></u><br><ul>
<li>When passing out rent increases, please make sure to also <strong> update AppFolio</strong>, so that
  each tenant's monthly reoccuring charges reflect the updated rent amount!</li>
<li>POH rent increases take effect twice each year: Feb 1st & August 1st</li>
<li>Annual TOH Increases take effect on the following dates: 
         <ul>
         <li> Crestview: Jan 1st</li> 
         <li> Holiday: Feb 1st</li>
         <li> Mt Vista: Feb 1st</li>
         <li> Hitching: Jul 1st</li>
        <li>  Westwind: July 1st</li>
         <li> Wishing: Oct 1st</li>
         </ul>
         </ul>
*If you see any discrepencies, please call Victor</p>'''

    emailbody = emailbody + POHbody+ TOHbody+'\n'+Tailbody
    return emailbody

def sendemail():
    POHoutput = r'C:\Users\Lenovo\PycharmProjects\rentincrease\venv\POHoutput.csv'
    TOHoutput = r'C:\Users\Lenovo\PycharmProjects\rentincrease\venv\TOHoutput.csv'
    eligiblePOH = r'C:\Users\Lenovo\PycharmProjects\rentincrease\venv\eligiblePOH.csv'
    eligibleTOH = r'C:\Users\Lenovo\PycharmProjects\rentincrease\venv\eligibleTOH.csv'
    emailtitle = convertdate(dateinput)+': Rent Increases That Need To Be Passed Out This Month'

    if areanyPOHeligible4increase() and areanyTOHeligible4increase():
        ezgmail.send('vchen2120@gmail.com', emailtitle, emailbody(), [POHoutput, eligiblePOH,TOHoutput,eligibleTOH],mimeSubtype='html')
    if areanyPOHeligible4increase() and not areanyTOHeligible4increase():
        ezgmail.send('vchen2120@gmail.com', emailtitle, emailbody(), [POHoutput, eligiblePOH],mimeSubtype='html')
    if not areanyPOHeligible4increase() and areanyTOHeligible4increase():
        ezgmail.send('vchen2120@gmail.com', emailtitle, emailbody(), [TOHoutput, eligibleTOH],mimeSubtype='html')
    if not areanyPOHeligible4increase() and not areanyTOHeligible4increase():
        ezgmail.send('vchen2120@gmail.com', emailtitle, emailbody(),mimeSubtype='html')
    print( 'Email Sent!')
    return None

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

#For TOH - Create a combined PDF for managers to fill out
def fill90daynotices():
    d = {'Tenant':'VChen','SpNum':'','Address':'','IncrDate':'','Year':'',
        'OrigRent':'','NewRent':'','Total_Incr':'','Date':'','ManagerName':''
    }
    #create a list of output PDFs, one for each complex
    ListOfOutputPaths = []
    for i in EligTOHlist():
        ListOfOutputPaths.append(r'C:\Users\Lenovo\PycharmProjects\rentincrease\venv\FillPDFs'+'\90daynotices_'+i+'.pdf')
    #(1) copy the page
    #(2) fill the page
    #(3) save the page in indiv_notices
    #(4) ... after looping (1-3) combine all pages in indiv_notices
    #(5) erase everything in indiv_notices

    #for each property, has its own PDF
    # for outputpath in ListOfOutputPaths:
    inputpath = r'C:\Users\Lenovo\PycharmProjects\rentincrease\venv\FillPDFs\90dayempty.pdf'

    #First: Dump everything into indiv_notices folder
    pdfs = []
    for x in range(10):
        reader = PdfFileReader(inputpath)
        writer = PdfFileWriter()
        pageobj = reader.getPage(0)
        writer.addPage(pageobj)
        writer.updatePageFormFieldValues(
            writer.getPage(0), {'Tenant': 'Victorino'}
        )
        outputpath = r'C:\Users\Lenovo\PycharmProjects\rentincrease\venv\FillPDFs\indiv_notices\Sp'+str(x)+'.pdf'
        pdfs.append(outputpath)
        pdfOutputFile = open(outputpath,'wb')
        writer.write(pdfOutputFile)
        pdfOutputFile.close()

    #Second: combine everything in indiv_notices folder
    # merger = PdfFileMerger()
    from pdf2image import convert_from_path
    from PIL import Image
    pop_path = r'C:\Users\Lenovo\PycharmProjects\rentincrease\venv\Lib\site-packages\poppler'

    os.chdir(r'C:\Users\Lenovo\PycharmProjects\rentincrease\venv\Lib\site-packages\poppler_utils-0.1.0.dist-info')
    for pdf in pdfs:
        images = convert_from_path(pdf,poppler_path=pop_path)
        im1 = images[0]
        images.pop(0)

        pdf1_filename = str(pdfs.index(pdf))+'.pdf'
        im1.save(pdf1_filename, "PDF", resolution=100.0, save_all=True, append_images=images)
        # merger.append(PdfFileReader(open(pdf,'rb')))
    # merger.write(r'C:\Users\Lenovo\PycharmProjects\rentincrease\venv\FillPDFs\combined.pdf')

# fill90daynotices()

#ink autocad PDF drawing with those sweet, sweet labels on bottom left hand corner
def ink_drawing():
    d = {'Tenant': 'VChen', 'SpNum': '50', 'Address': '34184 County Line Rd, Space 99',
         'IncrDate': '07/01/2022', 'Year': '22',
         'OrigRent': '700', 'NewRent': '900', 'Total_Incr': '200', 'Date': '05/01/2022', 'ManagerName': 'Brian Nguyen'
         }
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=letter)
    can.drawString(100, 623, d['Tenant'])
    can.drawString(158, 597, d['SpNum'])
    can.drawString(320, 597, d['Address'])
    can.drawString(265, 530, d['IncrDate'])
    can.drawString(408, 530, d['Year'])
    can.drawString(340, 488, d['OrigRent'])
    can.drawString(480, 488, d['NewRent'])
    can.drawString(500, 380, d['NewRent'])
    can.drawString(500, 300, d['NewRent'])
    can.drawString(400, 125, d['ManagerName'])
    can.drawString(80, 423, d['Total_Incr'])
    can.drawString(330, 172, d['Year'])
    can.drawString(180, 172, d['Date'])
    s1 = "Footprint-- "
    s2 = "Lot-- "
    s3 = 'Building_SF'
    can.drawString(10, 40, s1)
    can.drawString(10, 25, s2)
    can.drawString(10, 10, s3)
    can.save()

    #move to the beginning of the StringIO buffer
    packet.seek(0)

    # create a new PDF with Reportlab
    new_pdf = PdfFileReader(packet)
    # read your existing PDF
    input_path = r'C:\Users\Lenovo\PycharmProjects\rentincrease\venv\FillPDFs\90dayempty.pdf'
    output_path = r'C:\Users\Lenovo\PycharmProjects\rentincrease\venv\FillPDFs\indiv_notices\Sp0inked.pdf'

    existing_pdf = PdfFileReader(open(input_path, "rb"))
    output = PdfFileWriter()
    # add the "watermark" (which is the new pdf) on the existing page
    page = existing_pdf.getPage(0)
    page.mergePage(new_pdf.getPage(0))
    output.addPage(page)
    # finally, write "output" to a real file
    outputStream = open(output_path, "wb")
    output.write(outputStream)
    outputStream.close()

ink_drawing()
#send the email to all prop managers
sendemail()
