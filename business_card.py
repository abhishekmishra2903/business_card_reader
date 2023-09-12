# importing necessary libraries

import streamlit as st
import pandas as pd
import easyocr
import re
import mysql.connector

# establishing sql connection (put your own password)

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="**********",
auth_plugin='mysql_native_password'
)
mycursor = mydb.cursor()
mycursor.execute("set autocommit=1")
mycursor.execute('USE card')

# setting up the streamlit page

st.header('	:ticket: Data storage for Business-cards')
st.markdown('<style>div.block-container{padding-top:2rem;}</style>',unsafe_allow_html=True)
mode = st.sidebar.radio("Select the mode",['Upload','View/Delete'],horizontal=True)

# In upload mode we facilitate uploading of card image, then verification of
# details and finally saving it to sql database.

if mode=='Upload':
    uploaded_image=st.file_uploader('Upload a clear business_card image',type=['.png','.jpg','.jpeg'])
    if uploaded_image is not None:
        
# widget to upload image of business card        
        
        st.image(uploaded_image,width=550)
        
# converting uploaded image to bytes, to be uploaded to sql            
            
        bytes_data=uploaded_image.getvalue()

# using OCR library to get the relevant data from the image

        reader=easyocr.Reader(['en'],gpu=False)
#        result=reader.readtext(os.path.join("C:/Users/Admin/Documents/Project_business_card/",uploaded_image.name))
        result=reader.readtext(bytes_data)
        data_list=[]
        for i in range(len(result)):
             data_list.append(result[i][1])

# Creating an empty dictionary of fields with default value None.
                
        data_dict={'Company_name':None, 'Cardholder_name':None, 'Designation':None, 'Mobile_number':None, 'Email_address':None, 'Website_URL':None, 'Area':None, 'City':None, 'State':None, 'Pin_code':None}
        
# Cardholder_name and designation are invariably 1st two entries of data_list
# So filling our data_dict accordingly and simultaneously popping values from 
# the list to reduce complexity in identifying other fields.        
        
        data_dict['Cardholder_name']=data_list[0]
        data_dict['Designation']=data_list[1]
        data_list.pop(0)
        data_list.pop(0)

# identifying email address with the '@' symbol

        for i in data_list:
            if '@' in [*i]:
                data_dict['Email_address']=i
                data_list.remove(i)
                break
 
# identifying mobile number by assuming that the string would only consist of
# + - or number
               
        for i in data_list:
            test=True
            for j in [*i]:
                if j not in ['+','-','1','2','3','4','5','6','7','8','9','0']:
                    test=False
            if test==True and (len(i)>7):
                data_dict['Mobile_number']=i
                data_list.remove(i)
                break

# Removing any other number from the list if any

        for i in data_list:
            test=True
            for j in [*i]:
                if j not in ['+','-','1','2','3','4','5','6','7','8','9','0']:
                    test=False
            if test==True and (len(i)>7):
                data_list.remove(i)

# Identifying website by looking for strings trailing with 'com'

        for i in data_list:
            if i[-3::]=='com':
                website=i
                break
# Handling situation where dot has not been recognized or read as empty space
        if website[-4]==' ':
            website=website[0:-4]+'.com'
        elif website[-4] not in [' ','.']:
            website=website[0:-3]+'.com'

# Handling situation where dot has gone missing after www and where www has 
# gone to a separate string

        if website[0:3].lower()=='www' and website[3]==' ':
            website='www.'+ website[4:]
        elif website[0:3].lower()!='www' and website[0]!='.':
            website='www.'+website
            for i in data_list:
                if i.lower().strip()=='www':
                    data_list.remove(i)
                
        if website[0:3]!='www':
            website='www' + website[3:]
            
        data_dict['Website_URL']=website

# removing the field for website from data_dict

        for i in data_list:
            if i[-3::]=='com':
                data_list.remove(i)
                break

# identifying string which consists only numbers i.e. pin code

        for i in data_list:
            switch=True
            for j in [*i]:
                if j not in ['1','2','3','4','5','6','7','8','9','0']:
                    switch=False
                    break
            if switch==True:
                data_dict['Pin_code']=i
                data_list.remove(i)
                
# if after removal of pin code only two strings are left in the list. Then second
# string is the company name and first is the address block.                
                
            if switch==True and len(data_list)==2:
                data_dict['Company_name']=data_list[1]
                address= re.split(r',|;',data_list[0])
                
# removing empty strings from address                
                
                for i in address:
                    if i=='':
                        address.remove(i)
                        
# identifying state, city and area in order                        
                        
                data_dict['State']=address[-1]
                address.pop(-1)
                data_dict['City']=address[-1]
                address.pop(-1)
                data_dict['Area']=''.join(address)
                data_list.clear()
                
# if after removal of pin code, there are three strings left then the 1st string
# is the address and the rest two is company's name.            
            
            elif switch==True and len(data_list)==3:
                data_dict['Company_name']=data_list[1]+' '+data_list[2]
                address= re.split(r',|;',data_list[0])
                
# removing empty strings from address                
                
                for i in address:
                    if i=='':
                        address.remove(i)
                        
# identifying state, city and area in order  
                        
                data_dict['State']=address[-1]
                data_dict['City']=address[-2]
                address.pop(-1)
                address.pop(-1)
                data_dict['Area']=''.join(address)
                data_list.clear()
                
# identifying string that contains pin code. Such string consists state's name
# along with pin, so splitting them.                
                
        for i in data_list:
            k=0
            for j in [*i]:
                if j in ['1','2','3','4','5','6','7','8','9','0']:
                    k=k+1
            if k>5:
                data_dict['State']=i.split()[0]
                data_dict['Pin_code']=i.split()[1]
                data_list.remove(i)
 
# if 3 strings are remaining then 1st is address and 2nd 3rd are company's name               
 
        if len(data_list)==3:
            data_dict['Company_name']=data_list[1]+' '+data_list[2]
            address= re.split(r',|;',data_list[0])
            
# removing empty strings and identifying city and area            
            
            for i in address:
                if i=='':
                    address.remove(i)
            data_dict['City']=address[-1]
            address.pop(-1)
            data_dict['Area']=''.join(address)
            
# if there are more than 3 strings then Area and City are separate            
            
        if len(data_list)>3:
            data_dict['Area']=data_list[0]
            data_dict['City']=data_list[1]
            data_dict['Company_name']=data_list[2]+' '+data_list[3]
        
# Will append all fields in the list below and then execute with sql to update
# all fields in the database        
        
        verified_data=[bytes_data]
        
# showing the ocr result in sidebar and appending the entries in above list, once
# submit button is clicked        
        
        st.sidebar.write('Please verify the entries:')
        with st.sidebar.form('key123',clear_on_submit=False):
            cname=st.text_input("Company-name",value=data_dict['Company_name'])
            name=st.text_input("Cardholder-name",value=data_dict['Cardholder_name'])
            desig=st.text_input("Designation",value=data_dict['Designation'])
            mobile=st.text_input("Mobile-number",value=data_dict['Mobile_number'])
            mail=st.text_input("Email-address",value=data_dict['Email_address'])
            web=st.text_input("Website-URL",value=data_dict['Website_URL'])
            area=st.text_input("Area",value=data_dict['Area'])
            city=st.text_input("City",value=data_dict['City'])
            state=st.text_input("State",value=data_dict['State'])
            pin=st.text_input("Pin_code",value=data_dict['Pin_code'])
            submitted = st.form_submit_button("Click to save data in SQL server")
            if submitted:
                verified_data.append(cname)
                verified_data.append(name)
                verified_data.append(desig)
                verified_data.append(mobile)
                verified_data.append(mail)
                verified_data.append(web)
                verified_data.append(area)
                verified_data.append(city)
                verified_data.append(state)
                verified_data.append(pin)

# To avoid duplication we are checking if the mailID is already in database. Giving
# warning if data is already there, else updating the data
                
                mail=mail.lower()
                mail=mail.strip()
                mail_test=[]
                mycursor.execute("select Email_address from business_card")
                for i in mycursor:
                    mail_test.append(i[0])
                mail_test=[i.lower() for i in mail_test]
                mail_test=[i.strip() for i in mail_test]
                
                if mail not in mail_test:
                    sql=("insert into business_card (image,Company_name,Cardholder_name,Designation,Mobile_number,Email_address,Website_URL,Area,City,State,Pin_code) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)")
                    mycursor.execute(sql,verified_data)
                    st.warning('Data successfully uploaded')
                else:
                    st.warning("Data already present. Please click on 'View/Delete' button to update the data", icon= "🚨")

# in View/Delete mode the user can delete his data from the database or can
# just see the details
# Taking mailID as input from the user to fetch his data.
        
if mode=='View/Delete':
    mail_input=st.text_input('Please enter your email_address',value='xyz@mail.com')
    mail_input=mail_input.lower()
    mail_input=mail_input.strip()
    
    mail_test=[]
    mycursor.execute("select Email_address from business_card")
    for i in mycursor:
        mail_test.append(i[0])
    mail_test=[i.lower() for i in mail_test]
    mail_test=[i.strip() for i in mail_test]
    
    if mail_input != 'xyz@mail.com':
        if mail_input not in mail_test:
            st.warning("Data not in database. Please upload data by clicking on 'Upload' button", icon="⚠️")
        else:
            
# Fetching image and showing on dashboard            
            
            sql=("select Image from business_card where Email_address= %s ")
            mycursor.execute(sql,[mail_input])
            for i in mycursor:
                fetched_image=i[0]
            st.image(fetched_image,width=550)
            
# Fetching other details and showing in a dataframe format            
            
            sql=("select Company_name,Cardholder_name,Designation,Mobile_number,Email_address,Website_URL,Area,City,State,Pin_code from business_card where Email_address= %s")
            mycursor.execute(sql,[mail_input])
            fields=['Company_name','Cardholder_name','Designation','Mobile_number','Email_address','Website_URL','Area','City','State','Pin_code']
            entry_list=[]
            for i in mycursor:
                for j in range(10):
                    entry_list.append(i[j])
            df_dict=dict(Fields=fields,Entries=entry_list)
            df=pd.DataFrame(df_dict)
            st.sidebar.dataframe(df)
            
# Providing a button to delete the data from the database.            
            
            delete_data = st.sidebar.button('Delete your data from the database')
            if delete_data==True:
                sql=("delete from business_card where Email_address= %s ")
                mycursor.execute(sql,[mail_input])
                st.warning('Your data has been deleted successfully. You can switch to Upload mode to save a fresh copy',icon= "🚨")
