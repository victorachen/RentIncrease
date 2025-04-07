#script was running inconsistently so cleaned it up with Chatgpt to ensure
#more consistent run times

import datetime
import os
import ezgmail
import logging
import csv
from csv import writer
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from PyPDF2 import PdfFileWriter, PdfFileReader, PdfFileMerger

# Set working directory
os.chdir(r'C:\Users\19097\PycharmProjects\rentincrease')
ezgmail.init()

# Logging setup
log_path = 'email_log.txt'
logging.basicConfig(filename=log_path, level=logging.INFO, format='%(asctime)s - %(message)s')

# Today's date
dateinput = datetime.date.today()
today = datetime.date.today()
month_name = today.strftime('%B')
year = today.year

# Email title
email_title = f"{month_name} {year}: Rent Increases Reminder"

# Flag file to track if email was sent this month
flag_file = f'.sentflag_{today.strftime("%Y-%m")}.txt'

def Xmonthsfromnow(x, dateinput):
    day = dateinput.day
    this_month = dateinput.month
    this_year = dateinput.year
    month = (this_month + x - 1) % 12 + 1
    year = this_year + (this_month + x - 1) // 12
    return f"{month}/{day}/{year}"

def convertdate(date):
    D = {1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun',
         7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'}
    return f"{D[date.month]} {date.year}"

def emailbody():
    TOH_Dic_90daysprior = {
        'Hitching Post': 3, 'Wishing Well': 7, 'Holiday': 10, 'Mt Vista': 10, 'Crestview': 1,
        'Westwind': 3, 'Avalon': 8, 'Aladdin': 6, 'Bonanza': 4
    }

    body = f"Rent increases we need to pass out this month ({convertdate(dateinput)}):\n\n"

    if dateinput.month == 6 or dateinput.month == 11:
        body += "(1) POH: Avalon, Aladdin, Bonanza, Hitching Post, Wishing Well, Holiday, Mt Vista, Crestview, Patrician, Westwind, & some Single Family Homes need 30 day notices passed out this month\n"
    else:
        body += "(1) POH: No increases to pass out this month!\n"

    toh_props = [p for p in TOH_Dic_90daysprior if TOH_Dic_90daysprior[p] == dateinput.month]
    if toh_props:
        props_list = ", ".join(toh_props)
        body += f"(2) TOH: {props_list} need 90 day notices passed out this month -- Increase To Take Effect {Xmonthsfromnow(4, dateinput)}\n(See 'eligibleTOH.csv' for a list of TOH tenants needing increases)\n"
    else:
        body += "(2) TOH: No increases to pass out this month!\n"

    body += (
        "\nNotes:\n\n"
        "When passing out rent increases, please make sure to also update AppFolio, so that each tenant's monthly reoccuring charges reflect the updated rent amount!\n"
        "POH rent increases take effect twice each year: Feb 1st (pass out 30-day by Dec 31) & Aug 1st (pass out 30-day by June 30)\n"
        "Annual TOH Increases take effect on the following dates:\n"
        "Crestview: May 1st (Kim Everts requests packet by Jan 10; Pass out 90-day by Jan 30)\n"
        "Holiday: Feb 1st (Kim Everts requests packet by Oct 10; Pass out 90-day by Oct 31)\n"
        "Mt Vista: Feb 1st (Kim Everts requests packet by Oct 10; Pass out 90-day by Oct 31)\n"
        "Hitching: Jul 1st (Kim Everts requests packet by Mar 10; Pass out 90-day by Mar 31)\n"
        "Westwind: Jul 1st (Kim Everts requests packet by Mar 10; Pass out 90-day by Mar 31)\n"
        "Bonanza: Aug 1st (Kim Everts requests packet by Apr 10; Pass out 90-day by Apr 30)\n"
        "Aladdin: Oct 1st (Kim Everts requests packet by Jun 10; Pass out 90-day by Jun 30)\n"
        "Wishing: Nov 1st (Kim Everts requests packet by Jul 10; Pass out 90-day by Jul 31)\n"
        "Avalon: Dec 1st (Kim Everts requests packet by Aug 10; Pass out 90-day by Aug 31)\n"
        "*If you see any discrepancies, please call Victor\n"
    )
    return body

def already_sent_this_month():
    return os.path.exists(flag_file)

def mark_as_sent():
    with open(flag_file, 'w') as f:
        f.write(f'Sent at {datetime.datetime.now()}')

def DownloadRentRoll():
    resultsThreads = ezgmail.search('Automate Rent Increase')
    mostrecentemail = resultsThreads[0]
    downloadfolder = r'C:\Users\19097\PycharmProjects\rentincrease\venv'
    mostrecentemail.messages[0].downloadAllAttachments(downloadFolder=downloadfolder)
    todaystr = str(datetime.date.today()).replace('-', '')
    oldname = rf'{downloadfolder}\rent_roll-{todaystr}.csv'
    newname = rf'{downloadfolder}\rentroll.csv'
    if os.path.exists(oldname):
        os.rename(oldname, newname)

def GetData():
    path = r'C:\Users\19097\PycharmProjects\rentincrease\venv\rentroll.csv'
    with open(path) as file:
        reader = csv.reader(file)
        return list(reader)

def run_rent_increase_workflow():
    fname = r'C:\Users\19097\PycharmProjects\rentincrease\venv\rentroll.csv'
    if os.path.isfile(fname):
        os.remove(fname)

    DownloadRentRoll()
    data = GetData()
    logging.info("Rent increase workflow completed.")

if __name__ == "__main__":
    email_body = emailbody()

    if not already_sent_this_month():
        print("\n==== Rent Increase Email Body Preview ====")
        print(email_body)
        print("==== End of Preview ====")

        emaillist = ['vchen2120@gmail.com', 'vac56@cornell.edu', 'mt.vista.manager717@gmail.com',
                     'jessicachowchen@yahoo.com', 'jianchen20042005@yahoo.com', 'askrich@verizon.net',
                     'holiday34184@gmail.com', 'yucaipawestwind@gmail.com',
                     'hitchingpostmanager@gmail.com', 'patricianmhp@gmail.com', 'aladdinmanager9@gmail.com',
                     'manageravalon7@gmail.com', 'bonanza.mhp.manager@gmail.com', 'crestviewmhpmanager@gmail.com',
                     'wishingwellmanager@gmail.com', 'mt.vista.manager717@gmail.com', 'brianchen1321@gmail.com']

        try:
            for email in emaillist:
                ezgmail.send(
                    recipient=email,
                    subject=email_title,
                    body=email_body,
                    mimeSubtype='plain'
                )
            mark_as_sent()
            logging.info("Reminder email sent successfully to all recipients.")
        except Exception as e:
            logging.error(f"Failed to send reminder email to one or more recipients: {e}")

        run_rent_increase_workflow()
    else:
        logging.info("Email already sent this month. Skipping.")
        print("Email already sent this month. Skipping.")
        print("\n==== Rent Increase Email Body (Hypothetical Preview) ====")
        print(email_body)
        print("==== End of Hypothetical Preview ====")



#human code below
##to do: i don't think it needs to fill pdf's, just serve as a reminder
##ready to go: test out a bunch of diff dates, then set dateinput to today()
##
##import datetime
##dateinput = datetime.date.today()
## from datetime import datetime
## dateinput = datetime(2024,1,1)
##
##from PyPDF2 import PdfFileWriter, PdfFileReader, PdfFileMerger
##from datetime import date, datetime
##today = date.today()
## print(dateinput==today)
##
##import csv, ezgmail, os, io
##import os.path
##from csv import writer
##from reportlab.pdfgen import canvas
##from reportlab.lib.pagesizes import letter
##os.chdir(r'C:\Users\19097\PycharmProjects\rentincrease')
##ezgmail.init()
##
##return the date 3 months from dateinput
##def Xmonthsfromnow(x,dateinput):
##    day = dateinput.day
##    this_month = dateinput.month
##    this_year = dateinput.year
##    inc = x
##    month = (this_month + inc - 1) % 12 + 1
##    year = this_year + (this_month + inc - 1) // 12
##    #return the end result as a string, so we can compare with getstrtoday()
##    combined = str(month)+'/'+str(day)+'/'+str(year)
##    return combined
##
##convert "2023-10-01" to string "October 2023"
##def convertdate(date):
##    D = {1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun',
##                 7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'}
##    month = date.month
##    mapped_month = D[month]
##    year = date.year
##    combined = mapped_month + " "+ str(year)
##    return combined
##
## rentincreasedate = Xmonthsfromnow(2)
##proplist = ['Holiday', 'Mt Vista', 'Westwind', 'Avalon','Aladdin','Bonanza', 'Crestview', \
##         'Hitching Post', 'Patrician', 'Wishing Well', 'SFH']
##
##2 arguments: (1) property - ie) 'Holiday' and (2) attribute - ie)'Park Name'
##(1) Park Name (2) LLC (3) Number of Spaces
##def PropertyAttributeMapper(property,attribute):
##    d = {
##        'Holiday': {'Park Name':'Holiday Rancho', 'LLC':'Holiday Rancho Mobile Home Park, LLC','Num_Spaces': 128,'Address':'34184 County Line Rd'},
##        'Mt Vista': {'Park Name': 'Mt Vista', 'LLC': 'Mount Vista, LLC', 'Num_Spaces': 59,'Address':'13061 2nd St'},
##        'Westwind': {'Park Name': 'Westwind Estates', 'LLC': 'Yucaipa Westwind Estates, LLC', 'Num_Spaces': 87,'Address':'12380 4th St'},
##        'Crestview': {'Park Name': 'Crestview', 'LLC': 'Yucaipa Crestview, LLC', 'Num_Spaces': 55, 'Address':'12821 4th St'},
##        'Hitching Post': {'Park Name': 'Hitching Post', 'LLC': 'Hitching Post Mobile Home Park, LLC', 'Num_Spaces': 111, 'Address':'34642 Yucaipa Blvd'},
##        'Wishing Well': {'Park Name': 'Wishing Well', 'LLC': 'Wishing Well Mobile Home Park, LLC', 'Num_Spaces': 73, 'Address':'13063 5th St'},
##        'Avalon':{'Park Name': 'Avalon', 'LLC': 'Avalon Mobile Home Park', 'Num_Spaces': 86, 'Address':'35011 Avenue E'},
##        'Aladdin':{'Park Name': 'Aladdin', 'LLC': 'Aladdin Mobile Home Park', 'Num_Spaces': 97, 'Address':'12813 7th St'},
##        'Bonanza':{'Park Name': 'Bonanza', 'LLC': 'Bonanza Mobile Home Park', 'Num_Spaces': 83, 'Address':'13645 5th St'}
##    }
##    return d[property][attribute]
##
##given a property (string), abbreviate it (or group it into broader category [like 'SFH'])
##def abbr_prop(longpropname):
##    SFH_list = ['Chestnut','Elm','12398 4th','12993 2nd','Reedywoods','North Grove',\
##                'Massachusetts','Michigan','906 N 4th','Indian School','Cottonwood']
##    for i in SFH_list:
##        if i in longpropname:
##            return 'SFH'
##    for i in proplist:
##        if i in longpropname:
##            return i
##    return 'No prop found'
##
##2023 update: Now implementing this!
## abbreviate name of complex for txt msg. takes in full name of unit & returns abbr unit name string
##def abbr_complex(longpropname):
##    L = ['Holiday Rancho', 'Mt Vista', 'Westwind', 'Avalon', 'Aladdin', 'Bonanza', 'Crestview', \
##     'Hitching Post', 'Patrician', 'Wishing Well', 'SFH']
##    for i in L:
##        if i in longpropname:
##            return i
##    return 'None'
##
##given a list, return whether (that row) is a tenant
##def istenant(r):
##    if len(r)<4:
##        return False
##    if len(r[3])>3 and r[4]=='Current':
##        return True
##given a list, return whether (that row) is one of our props
##def isprop(r):
##    if len(r)<1:
##        return False
##    if len(r[0])>15:
##        return True
##
##2023 Edit: Avalon, Aladdin, Bonanza have some POH that charge really low rents
##this function return the low rent POH that may be exceptions to the rule of <$600/monthly rent
##def POH_exceptions(r,prop):
##    abbr_prop = abbr_complex(prop)
##
##    unit_num = str(r[0])
##    d = {'Avalon':['Apartment','1','6','7','16','17','22','28','32','40','41','43','44','47','48','52','54','59','61','69','77','83','85'],
##         'Aladdin':['6','8','21','29','39','43','45','46','53','55','56','58','60','64','77','86','88','90','95'],
##         'Bonanza':['82'],
##         'Wishing Well':['2','32','40','42','44','57','59']}
##    if abbr_prop in d:
##        if unit_num in d[abbr_prop]:
##            return True
##    return False
##
##given a list, return whether (that row) is a POH tenant
##def isPOH(r,prop):
##    rent = int(r[7].partition('.')[0].replace(',',''))
##    if rent>599 or POH_exceptions(r,prop):
##        return True
##    else:
##        return False
##
##def days_between(currentrentincrease, lastrentincrease):
##    currentrentincrease = datetime.strptime(currentrentincrease,"%m/%d/%Y")
##    lastrentincrease = datetime.strptime(lastrentincrease, "%m/%d/%Y")
##    return abs((currentrentincrease - lastrentincrease).days)
##
##def timesincelastinc(r,tenant_type):
##    if tenant_type == 'POH':
##        rentincreasedate = Xmonthsfromnow(2,dateinput)
##    if tenant_type == 'TOH':
##        rentincreasedate = Xmonthsfromnow(4,dateinput)
##    timediff = ''
##    if len(r[6])>1:
##        return days_between(rentincreasedate,r[6])
##    #if there is no recorded last rent increase, then use the move-in date
##    return days_between(rentincreasedate,r[5])
##
##given a list, return whether (that row) is Eligible for rent increase
##def isEligible(r,tenant_type,prop):
##    if timesincelastinc(r,tenant_type)>=330:
##        return 'Is Eligible'
##    #2023 Edit: Make Exceptions for Avalon, Aladdin, Bon (Increase rent anyway!)
##    if prop == 'Avalon' or prop == 'Aladdin' or prop == 'Bonanza':
##        return 'Is Eligible'
##    return ''
##
##def alterPOH(data):
##    prop = 'no prop'
##    for r in data:
##        if isprop(r):
##            prop = r[0]
##        if istenant(r):
##            # populate column I
##            r.append(abbr_prop(prop))
##            # populate column J
##            if isPOH(r,prop):
##                r.append('POH')
##            # populate column K
##                r.append(timesincelastinc(r,'POH'))
##                r.append(isEligible(r,'POH',abbr_complex(prop)))
##            else:
##                r.append('Tenant Owned')
##    return data
##
##copied pasta'd from above (fingers crossed it works)
##def alterTOH(data):
##    prop = 'no prop'
##    for r in data:
##        if isprop(r):
##            prop = r[0]
##        if istenant(r):
##            # populate column I
##            r.append(abbr_prop(prop))
##            # populate column J
##            if not isPOH(r,prop):
##
##                # 2023 Edit: Avalon, Aladdin, Bonanza exceptions to cheap POH
##                if POH_exceptions(r, prop):
##                    r.append('POH')
##
##                else:
##                    r.append('Tenant Owned')
##
##                # populate column K
##                r.append(timesincelastinc(r,'TOH'))
##                r.append(isEligible(r,'TOH',abbr_complex(prop)))
##            else:
##                r.append('POH')
##    return data
##
##Helper function: loop thru data set to create new csv --> export new csv to --> output_path
##def NewCsv(data,path):
##    output = open(path,'w',newline='')
##    writer = csv.writer(output)
##    for r in data:
##        writer.writerow(r)
##    output.close()
##
##clear any given CSV
##def clearCSV(path):
##    filename = path
##    # opening the file with w+ mode truncates the file
##    f = open(filename, "w+")
##    f.close()
##
##Takes in a row r (as a list), and maps elements of r into "90dayempty.pdf"
##create a crap ton of inked PDF drawings from input file "90dayempty.pdf", combining them into one PDF
##def ink_drawing(r):
##    d = {'Tenant': r[3], 'SpNum': r[0], 'Address': PropertyAttributeMapper(r[8],'Address'),
##         'IncrDate': Xmonthsfromnow(4,dateinput), 'Year': Xmonthsfromnow(4,dateinput)[-2:],
##         'OrigRent': r[7], 'Date': str(dateinput)[-5:]
##         }
##    packet = io.BytesIO()
##    can = canvas.Canvas(packet, pagesize=letter)
##    can.drawString(100, 623, d['Tenant'])
##    can.drawString(158, 597, d['SpNum'])
##    can.drawString(320, 597, d['Address'])
##    can.drawString(265, 530, d['IncrDate'])
##    # can.drawString(408, 530, d['Year'])
##    can.drawString(340, 488, d['OrigRent'])
##    # can.drawString(480, 488, d['NewRent'])
##    # can.drawString(500, 380, d['NewRent'])
##    # can.drawString(500, 300, d['NewRent'])
##    # can.drawString(400, 125, d['ManagerName'])
##    # can.drawString(80, 423, d['Total_Incr'])
##    can.drawString(330, 172, d['Year'])
##    can.drawString(180, 172, d['Date'])
##    can.save()
##
##    #move to the beginning of the StringIO buffer
##    packet.seek(0)
##
##    # create a new PDF with Reportlab
##    new_pdf = PdfFileReader(packet)
##    # read your existing PDF
##    input_path = r'C:\Users\19097\PycharmProjects\rentincrease\venv\FillPDFs\90dayempty.pdf'
##    output_path = r'C:\Users\19097\PycharmProjects\rentincrease\venv\FillPDFs\indiv_notices\Inked_Sp'+str(r[0])+'.pdf'
##
##    existing_pdf = PdfFileReader(open(input_path, "rb"))
##    output = PdfFileWriter()
##    # add the "watermark" (which is the new pdf) on the existing page
##    page = existing_pdf.getPage(0)
##    page.mergePage(new_pdf.getPage(0))
##    output.addPage(page)
##    # finally, write "output" to a real file
##    outputStream = open(output_path, "wb")
##    output.write(outputStream)
##    outputStream.close()
##
##takes in property name: mapping that prop name to the file name ex) Westwindcombined.pdf
##def combinePDFs(prop,PDFlist):
##    # source_dir = 'C:/Users/Lenovo/PycharmProjects/rentincrease/venv/FillPDFs/indiv_notices/'
##    # merger = PdfFileMerger()
##    #
##    # for item in os.listdir(source_dir):
##    #     if item.endswith('pdf'):
##    #         # print(item)
##    #         merger.append(source_dir + item)
##    #
##    # merger.write(r'C:\Users\Lenovo\PycharmProjects\rentincrease\venv\FillPDFs\_'+prop+'_combined.pdf')
##    # merger.close()
##    merger = PdfFileMerger()
##    for SpNum in PDFlist:
##        file = r'C:\Users\19097\PycharmProjects\rentincrease\venv\FillPDFs\indiv_notices\Inked_Sp'+str(SpNum)+'.pdf'
##        merger.append(PdfFileReader(open(file, 'rb')))
##    merger.write(r'C:\Users\19097\PycharmProjects\rentincrease\venv\FillPDFs\Attach2Email\_'+prop+'_letters.pdf')
##    return None
##
##after combining, delete all the PDFs in the folder (clear the junk)
##def DeleteEverythingInFolder(path):
##    os.chdir(path)
##    mydir = path
##    filelist = [f for f in os.listdir(mydir)]
##    for f in filelist:
##        os.remove(os.path.join(mydir, f))
##    return None
##
##create CSV for eligible POH residents
##def eligiblePOH(data):
##    #first, clear the old junk from CSV file
##    path = r'C:\Users\19097\PycharmProjects\rentincrease\venv\eligiblePOH.csv'
##    clearCSV(path)
##
##    # title each column
##    titles = ['Unit #', '', 'Bd/Ba', 'Tenant', 'Status', 'Move-in', 'Last Increase', '$ Rent', 'Property',
##              'Type', 'Days Since Last Increase', 'Eligibility']
##    header = ['*Today is '+convertdate(dateinput)+'; below shows all POH tenants eligible for increase 90 days from now on ' + Xmonthsfromnow(2,dateinput)]
##    append_list_as_row(path, header)
##    append_list_as_row(path, titles)
##    append_list_as_row(path, [])
##
##    for p in proplist:
##        append_list_as_row(path,[p])
##        for r in data:
##            if istenant(r) and isPOH(r,p) and isEligible(r,'POH',abbr_complex(p)) == "Is Eligible" and r[8] in p:
##                append_list_as_row(path,r)
##    return None
##
## Dictionary representing which months can push out Rent Increase for TOH
##TOH_Dic = {'Hitching Post': 7, 'Wishing Well': 11, 'Holiday': 2, 'Mt Vista': 2, 'Crestview': 5,'Westwind':7,'Avalon':12,'Aladdin':10,'Bonanza':8}
##Second Dic: ex) if hitching rent increase takes place in month 7, send out notif email during month 3
##TOH_Dic_90daysprior = {'Hitching Post': 3, 'Wishing Well': 7, 'Holiday': 10, 'Mt Vista': 10, 'Crestview': 1,'Westwind':3,'Avalon':8,'Aladdin':6,'Bonanza':4}
##
##helper for EligibleTOH() -- return list (eligibleTOHproplist) of props where it is time (this month) to pass out 90 days
##def EligTOHlist():
##    L = []
##    for prop in TOH_Dic_90daysprior:
##        if TOH_Dic_90daysprior[prop] == dateinput.month:
##            L.append(prop)
##    return L
##
##create CSV for eligible TOH residents
##def eligibleTOH(data):
##    #first, clear the old junk from CSV file
##    path = r'C:\Users\19097\PycharmProjects\rentincrease\venv\eligibleTOH.csv'
##    clearCSV(path)
##
##    #title each column
##    titles=['Unit #','','Bd/Ba','Tenant','Status','Move-in','Last Increase','$ Rent','Property',
##            'Type','Days Since Last Increase','Eligibility']
##    header = ['*Today is '+convertdate(dateinput)+'; below shows all TOH tenants eligible for increase 90 days from now on' + Xmonthsfromnow(4,dateinput)]
##    append_list_as_row(path, header)
##    append_list_as_row(path,titles)
##    append_list_as_row(path,[])
##
##
##
##    for p in TOH_Dic:
##        if p in EligTOHlist():
##            #you're doing 2 things at once here and it's getting super confusing
##            PDFlist = []
##
##            append_list_as_row(path, [p])
##            for r in data:
##                if istenant(r) and not isPOH(r,p) and r[8] in p:
##                    append_list_as_row(path,r)
##
##                    # 2023 edit: eliminating this whole pdf business!!!!!
##
##                    #create a pdf for every TOH that deserves an increase
##                    # ink_drawing(r)
##                    # #create a list of PDFs that you want combinePDFs() to glue together
##                    # PDFlist.append(r[0])
##
##            # do the PDF business, for properties with TOH increase eligibility
##            # combinePDFs(p,PDFlist)
##            DeleteEverythingInFolder(r'C:\Users\19097\PycharmProjects\rentincrease\venv\FillPDFs\indiv_notices')
##
##        else:
##            append_list_as_row(path, [p+': No TOH Increases For This Month!'])
##
##    return None
##
##def append_list_as_row(file_name, list_of_elem):
##    # Open file in append mode
##    with open(file_name, 'a+', newline='') as write_obj:
##        # Create a writer object from csv module
##        csv_writer = writer(write_obj)
##        # Add contents of list as last row in the csv file
##        csv_writer.writerow(list_of_elem)
##
##helper for emailbody()
##def areanyTOHeligible4increase():
##    if dateinput.month in TOH_Dic_90daysprior.values():
##        return True
##    return False
##helpers for emailbody()
##def areanyPOHeligible4increase():
##    if dateinput.month == 6 or dateinput.month == 11:
##        return True
##    return False
##
##
##return the text of the email body as a string
##def emailbody():
##    emailbody = '''<p><u>Rent increases we need to pass out this month <strong>('''+ convertdate(dateinput) + ')</strong>:<br></u></p>'
##
##    #only pass out POH Rent Increases during beginning & middle of the year (Aug 1st [6] & Feb 1st [11])
##    if areanyPOHeligible4increase():
##        POHbody = '''<strong>(1)</strong> <em>POH</em>: <strong> Avalon, Aladdin, Bonanza, Hitching Post, Wishing Well, Holiday, Mt Vista, Crestview, Patrician, Westwind, & some Single Family Homes </strong> need 30 day notices passed out. Increase To Take Effect: <strong>''' + Xmonthsfromnow(2,dateinput)+"</strong>-- <br><em> (See 'eligiblePOH.csv' for a list of POH tenants needing increases)</em><br>"
##    else:
##        POHbody = '<strong>(1)</strong> <em> POH</em>: No increases to pass out this month!<br>'
##
##    ifTOHno = '\n <strong>(2) </strong> <em>TOH</em>:  No increases to pass out this month!<br>'
##    ifTOHyes = '''90 day notices passed out this month -- Increase To Take Effect <strong>''' + Xmonthsfromnow(4, dateinput) + '''</strong><br>
##<em>(See 'eligibleTOH.csv' for a list of TOH tenants needing increases)</em><br>'''
##    TOHbody = '<strong>(2)</strong> <em> TOH</em>: '
##
##    count = 0
##    for prop in TOH_Dic_90daysprior:
##        if dateinput.month == TOH_Dic_90daysprior[prop]:
##            TOHbody = TOHbody + '<strong>'+ prop + '</strong>'+', '
##            count+=1
##    if areanyTOHeligible4increase():
##        #gotta make sure this is grammatically correct, ya know
##        if count > 1:
##            TOHbody = TOHbody + 'need '+ ifTOHyes
##        if count <=1:
##            TOHbody = TOHbody + 'needs '+ifTOHyes
##    else:
##        TOHbody = ifTOHno
##
##    Tailbody = '''
##
##<p><u><strong>Notes: </strong></u><br><ul>
##<li>When passing out rent increases, please make sure to also <strong> update AppFolio</strong>, so that
##  each tenant's monthly reoccuring charges reflect the updated rent amount!</li>
##<li>POH rent increases take effect twice each year: Feb 1st (pass out 30-day by Dec 31) & Aug 1st (pass out 30-day by June 30)</li>
##<li>Annual TOH Increases take effect on the following dates: 
##         <ul>
##         <li> Crestview: May 1st (Kim Everts requests packet by Jan 10; Pass out 90-day by Jan 30)</li> 
##         <li> Holiday: Feb 1st (Kim Everts requests packet by Oct 10; Pass out 90-day by Oct 31)</li>
##         <li> Mt Vista: Feb 1st (Kim Everts requests packet by Oct 10; Pass out 90-day by Oct 31)</li>
##         <li> Hitching: Jul 1st (Kim Everts requests packet by Mar 10; Pass out 90-day by Mar 31)</li>
##        <li>  Westwind: Jul 1st (Kim Everts requests packet by Mar 10; Pass out 90-day by Mar 31)</li>
##        <li> Bonanza: Aug 1st (Kim Everts requests packet by Apr 10; Pass out 90-day by Apr 30)</li>
##        <li> Aladdin: Oct 1st (Kim Everts requests packet by Jun 10; Pass out 90-day by Jun 30)</li>
##         <li> Wishing: Nov 1st (Kim Everts requests packet by Jul 10; Pass out 90-day by Jul 31)</li>
##         <li> Avalon: Dec 1st (Kim Everts requests packet by Aug 10; Pass out 90-day by Aug 31)</li>
##         </ul> 
##         </ul>
##*If you see any discrepencies, please call Victor</p>'''
##
##    emailbody = emailbody + POHbody+ TOHbody+'\n'+Tailbody
##    return emailbody
##
##def sendemail():
##    #first, dump every PDF in the "Attach2Email" folder, into the list of stuff to email
##    PDFs = os.listdir(r'C:\Users\19097\PycharmProjects\rentincrease\venv\FillPDFs\Attach2Email')
##    for i in PDFs:
##        PDFs[PDFs.index(i)] = 'C:/Users/19097/PycharmProjects/rentincrease/venv/FillPDFs/Attach2Email/'+i
##    #Now, fpr the rest of the stuff
##    POHoutput = r'C:\Users\19097\PycharmProjects\rentincrease\venv\POHoutput.csv'
##    TOHoutput = r'C:\Users\19097\PycharmProjects\rentincrease\venv\TOHoutput.csv'
##    eligiblePOH = r'C:\Users\19097\PycharmProjects\rentincrease\venv\eligiblePOH.csv'
##    eligibleTOH = r'C:\Users\19097\PycharmProjects\rentincrease\venv\eligibleTOH.csv'
##    emailtitle = convertdate(dateinput)+': Rent Increases That Need To Be Passed Out This Month'
##
##    emaillist = ['vchen2120@gmail.com', 'vac56@cornell.edu', 'mt.vista.manager717@gmail.com', \
##                 'jessicachowchen@yahoo.com', 'jianchen20042005@yahoo.com', askrich@verizon.net', \
##                 'holiday34184@gmail.com', 'yucaipawestwind@gmail.com', \
##                 'hitchingpostmanager@gmail.com', 'patricianmhp@gmail.com', 'aladdinmanager9@gmail.com',\
##                 'manageravalon7@gmail.com','bonanza.mhp.manager@gmail.com','crestviewmhpmanager@gmail.com',\
##                 'wishingwellmanager@gmail.com','mt.vista.manager717@gmail.com','brianchen1321@gmail.com'
##                 ]
##    # emaillist = ['vchen2120@gmail.com']
##    for e in emaillist:
##        if areanyPOHeligible4increase() and areanyTOHeligible4increase():
##            ezgmail.send(e, emailtitle, emailbody(), PDFs+[POHoutput, eligiblePOH,TOHoutput,eligibleTOH],mimeSubtype='html')
##        if areanyPOHeligible4increase() and not areanyTOHeligible4increase():
##            ezgmail.send(e, emailtitle, emailbody(), PDFs+[POHoutput, eligiblePOH],mimeSubtype='html')
##        if not areanyPOHeligible4increase() and areanyTOHeligible4increase():
##            ezgmail.send(e, emailtitle, emailbody(), PDFs+[TOHoutput, eligibleTOH],mimeSubtype='html')
##        if not areanyPOHeligible4increase() and not areanyTOHeligible4increase():
##            ezgmail.send(e, emailtitle, emailbody(),mimeSubtype='html')
##
##    #After sending the email, delete all PDFs (reset for next time)
##    DeleteEverythingInFolder(r'C:\Users\19097\PycharmProjects\rentincrease\venv\FillPDFs\Attach2Email')
##    print( 'Email Sent!')
##    return None
##
##scrape victoreceipts@gmail.com for AppFolio's daily automated email
##def DownloadRentRoll():
##    resultsThreads = ezgmail.search('Automate Rent Increase')
##    mostrecentemail = resultsThreads[0]
##
##    #Download the csv into local directory
##    downloadfolder = r'C:\Users\19097\PycharmProjects\rentincrease\venv'
##    mostrecentemail.messages[0].downloadAllAttachments(downloadFolder=downloadfolder)
##    #Name the most recently downloaded rent roll (what you did just above) --> "rentroll.csv"
##    today = str(date.today()).replace('-','')
##    oldname = r'C:\Users\19097\PycharmProjects\rentincrease\venv\rent_roll-'+today+'.csv'
##    newname = r'C:\Users\19097\PycharmProjects\rentincrease\venv\rentroll.csv'
##    os.rename(oldname,newname)
##
##get data from Rent Roll
##def GetData():
##    path = r'C:\Users\19097\PycharmProjects\rentincrease\venv\rentroll.csv'
##    file = open(path)
##    reader = csv.reader(file)
##    data = list(reader)
##    return data
##
##Takes in data, and spits out list of dictionaries, one dictionary for each eligibleTOHproperty
##ie) [Westwind_TOH_Dic, Hitching_TOH_Dic]
##where Holiday_TOH_Dic = {'Holiday':'cityformpdfhelper','5':['Liliana Macias','316.95']}
##(Helper function for cityformpdf()
##def CityFormPdfHelper(data):
##    ListOfDics = []
##    for p in TOH_Dic:
##        if p in EligTOHlist():
##            #create a sep dictionary for each prop
##            Dic = {}
##            Dic[p] = 'cityformpdfhelper'
##            for r in data:
##                if istenant(r) and not isPOH(r,p) and r[8] in p:
##                    Dic[r[0]] = [r[0],r[3],r[7]]
##            #Add the Dic to the ListofDics
##            ListOfDics.append(Dic)
##    return ListOfDics
##
##Fill out "CityFormEmpty.pdf"
##def cityformpdf():
##
##    #write whatever is in Dictionary "d" to CityFormpdf
##    def pdfwriter(prop, d):
##        emptypath = r'C:\Users\19097\PycharmProjects\rentincrease\venv\FillPDFs\CityFormEmpty.pdf'
##        outputpath = 'C:/Users/19097/PycharmProjects/rentincrease/venv/FillPDFs/Attach2Email/'+abbr_complex(prop)+'_CityForm.pdf'
##        reader = PdfFileReader(emptypath)
##        writer = PdfFileWriter()
##        fields = reader.getFields()
##        page0 = reader.pages[0]
##        page1 = reader.pages[1]
##        page2 = reader.pages[2]
##        page3 = reader.pages[3]
##        page4 = reader.pages[4]
##        page5 = reader.pages[5]
##        writer.addPage(page0)
##        writer.addPage(page1)
##        writer.addPage(page2)
##        writer.addPage(page3)
##        writer.addPage(page4)
##        writer.addPage(page5)
##        # Now you add your data to the forms!
##        for x in d:
##            for p in range(6):
##                writer.updatePageFormFieldValues(
##                    writer.getPage(p), {x: d[x]})
##        # write "output" to PyPDF2-output.pdf
##        with open(outputpath, "wb") as output_stream:
##            writer.write(output_stream)
##
##    ListOfDics = CityFormPdfHelper(alterTOH(GetData()))
##    #where complexdic is dictionary of "Holiday" or "MtV" that has all the TOH unit data
##    for complexdic in ListOfDics:
##        for possiblecomplex in EligTOHlist():
##            if possiblecomplex in complexdic:
##                #sigh, create yet another dictionary that maps to "CityFormEmptyl.pdf"
##                d = {}
##                count = 0
##                for unit in complexdic:
##                    if unit not in proplist:
##                        count+= 1
##                        d["S"+str(count)] = complexdic[unit][0]
##                        d["T" + str(count)] = complexdic[unit][1]
##                        d["R" + str(count)] = complexdic[unit][2]
##
##                #Hard Code Other Stuff into D
##                #to do: map complex to (1) address, (2) llc, (3) total spaces, (4) total_toh_spaces
##                d['ParkName'] = possiblecomplex
##                d['Full_Address'] = PropertyAttributeMapper(possiblecomplex,'Address')+',Leasing Office, Yucaipa, CA 92399'
##                d['Day'] = str(datetime.today().day)
##                d['Month'] = ''.join([i for i in convertdate(datetime.today()) if not i.isdigit()])
##                d['Year'] = str(datetime.today().year)[-2:]
##                d['LLC'] = PropertyAttributeMapper(possiblecomplex,'LLC')
##                d['Short_Address'] = PropertyAttributeMapper(possiblecomplex,'Address')
##                d['total_park_spaces'] = PropertyAttributeMapper(possiblecomplex,'Num_Spaces')
##                d['total_toh_spaces'] = str(count)
##                d['curr_incr'] = str(Xmonthsfromnow(4, dateinput))
##                pdfwriter(possiblecomplex,d)
##                print(d)
##    return None
## cityformpdf()
##
##Before we start anything, let's delete all previous files in local directory named "rentroll.csv"
##fname = r'C:\Users\19097\PycharmProjects\rentincrease\venv\rentroll.csv'
##if os.path.isfile(fname):
##    os.remove(fname)
##Then, let's download a fresh rentroll from Appfolio
##DownloadRentRoll()
##
## Create POHoutput.csv
##POH_data = alterPOH(GetData())
##output_path = r'C:\Users\19097\PycharmProjects\rentincrease\venv\POHoutput.csv'
##NewCsv(POH_data, output_path)
##
##Create TOHoutput.csv
##TOH_data = alterTOH(GetData())
##output_path = r'C:\Users\19097\PycharmProjects\rentincrease\venv\TOHoutput.csv'
##NewCsv(TOH_data, output_path)
##
## Create eligiblePOH.csv
##eligiblePOH(POH_data)
##
##create eligibleTOH.csv
##eligibleTOH(TOH_data)
##
##send the email to all prop managers
##sendemail()
