import ezgmail, os
os.chdir(r'C:\Users\19097\PycharmProjects\arescriptsrunning')
ezgmail.init()

ezgmail.send('vchen2120@gmail.com','Scripts are running today :)',"Can't break me that easily :D")
print('email sent')
