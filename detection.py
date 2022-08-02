# STEP 1:importing modules
import cv2 as cv
from cv2 import approxPolyDP
import pytesseract
import mysql.connector
import smtplib

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="",
    port=3306,
    database="rto"#database name
)
cur = mydb.cursor()


pytesseract.pytesseract.tesseract_cmd=r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe'
#STEP 2:READING THE IMAGE AND CONVERTING INTO GRAYSCALE
image = cv.imread('car2.png')#place the image here
grey = cv.cvtColor(image,cv.COLOR_BGR2GRAY)

#STEP 3:detecting the edges
canny=cv.Canny(grey,170,200)

#STEP 4:finding the contours
cnt ,new= cv.findContours(canny.copy(),cv.RETR_LIST,cv.CHAIN_APPROX_SIMPLE)
#STEP 5:finding the maximum value from the countours
cnt=sorted(cnt, key=cv.contourArea ,reverse=True)[0:10]
#STEP 6:finding number plate
number=None
for c in cnt:
    peri = cv.arcLength(c,True)
    epsilon = 0.018*peri
    approx=approxPolyDP(c,epsilon,True)
    #STEP 7:if the approx has 4 sides we got the number plate
    if(len(approx)==4):
        number=approx
        x,y,w,h = cv.boundingRect(c)
        #STEP 8:this cropped image is our number plate
        crop=image[y:y+h ,x:x+w]
        break
#STEP 9:drawing green line outside the number plate
cv.drawContours(image,[number],-1,(0,255,0),3)
#CONVERTING THE IMAGE INTO A STRING
text = pytesseract.image_to_string(crop,lang='eng')
print(type(text))
print("Number :",text)
cv.imshow('detected',image)
cv.waitKey(0)

#STEP 10:changing the text to list format to access from the database
text1=[text]
text2=[x.replace('\n','') for x in text1]
text2=[x.replace(',','') for x in text2]
text2=[x.replace(' ','') for x in text2]
text2=[x.replace('|','') for x in text2]
text2=[x.replace("'",'') for x in text2]
text2=[x.replace('[','') for x in text2]
#STEP 11:EXTRACTING THE DETAILS FROM THE DATABASE
cur.execute("select * from owner_details where vehicle_number=%s",text2)
result = cur.fetchall()
#STEP 12:FETCHING THE INFORMATION FROM THE DATABASE AND PROVIDING THE INFO TO THE USER
print("Car Name :",result[0][1])
print("Model :",result[0][2])
print("year of registration :",result[0][3])
print("owner name :",result[0][4])
print("address :",result[0][6])
#STEP 13:FETCHING THE EMAIL FROM THE DATABASE FOR SENDING THE MESSAGE
cur.execute("select email from owner_details where vehicle_number=%s",text2)
mail=cur.fetchall()
#STEP 14:ENTER THE MESSAGE FOR SENDING TO THE OWNER IN CASE OF ANY EMERGENCIES
msg = input("enter the message to send :")
server = smtplib.SMTP_SSL('smtp.gmail.com',465)
server.login('senti.safi@gmail.com','sentisafi@123')
server.sendmail('senti.safi@gmail.com',mail[0][0],msg)
print("mail sent")
server.quit()
#PROGRAM ENDS
