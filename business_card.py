import streamlit as st
from PIL import Image
from io import BytesIO
import pandas as pd
import numpy as np
import cv2
import easyocr
import os
import re

import mysql.connector
mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="5115269000",
auth_plugin='mysql_native_password'
)
mycursor = mydb.cursor()
mycursor.execute("set autocommit=1")
mycursor.execute('USE card')


st.header('	:ticket: Data storage for Business-cards')
st.markdown('<style>div.block-container{padding-top:2rem;}</style>',unsafe_allow_html=True)

mode = st.sidebar.radio("Select the mode",['Upload','View/Delete'],horizontal=True)

if mode=='Upload':
    uploaded_image=st.file_uploader('Upload a clear business_card image',type=['.png','.jpg','.jpeg'])
    if uploaded_image is not None:
        st.image(uploaded_image,width=550)
    
#        with open(os.path.join("C:/Users/Admin/Documents/Project_business_card/",uploaded_image.name),"wb") as f:
#            f.write(uploaded_image.getbuffer())

        reader=easyocr.Reader(['en'],gpu=False)
        result=reader.readtext(os.path.join("C:/Users/Admin/Documents/Project_business_card/",uploaded_image.name))

        data_list=[]
        for i in range(len(result)):
            if type(result[i])==tuple:
                data_list.append(result[i][1])
                
        data_dict={'Company_name':None, 'Cardholder_name':None, 'Designation':None, 'Mobile_number':None, 'Email_address':None, 'Website_URL':None, 'Area':None, 'City':None, 'State':None, 'Pin_code':None}
        data_dict['Cardholder_name']=data_list[0]
        data_dict['Designation']=data_list[1]
        data_list.pop(0)
        data_list.pop(0)

        for i in data_list:
            if '@' in [*i]:
                data_dict['Email_address']=i
                data_list.remove(i)
                break
                
        for i in data_list:
            test=True
            for j in [*i]:
                if j not in ['+','-','1','2','3','4','5','6','7','8','9','0']:
                    test=False
            if test==True and (len(i)>7):
                data_dict['Mobile_number']=i
                data_list.remove(i)
                break

        for i in data_list:
            test=True
            for j in [*i]:
                if j not in ['+','-','1','2','3','4','5','6','7','8','9','0']:
                    test=False
            if test==True and (len(i)>7):
                data_list.remove(i)

        for i in data_list:
            if i[-3::]=='com':
                website=i
                break

        if website[-4]==' ':
            website=website[0:-4]+'.com'
        elif website[-4] not in [' ','.']:
            website=website[0:-3]+'.com'

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

        for i in data_list:
            if i[-3::]=='com':
                data_list.remove(i)
                break

        for i in data_list:
            switch=True
            for j in [*i]:
                if j not in ['1','2','3','4','5','6','7','8','9','0']:
                    switch=False
                    break
            if switch==True:
                data_dict['Pin_code']=i
                data_list.remove(i)
            if switch==True and len(data_list)==2:
                data_dict['Company_name']=data_list[1]
                address= re.split(r',|;',data_list[0])
                for i in address:
                    if i=='':
                        address.remove(i)
                data_dict['State']=address[-1]
                address.pop(-1)
                data_dict['City']=address[-1]
                address.pop(-1)
                data_dict['Area']=''.join(address)
                data_list.clear()
                
            elif switch==True and len(data_list)==3:
                data_dict['Company_name']=data_list[1]+' '+data_list[2]
                address= re.split(r',|;',data_list[0])
                for i in address:
                    if i=='':
                        address.remove(i)
                data_dict['State']=address[-1]
                data_dict['City']=address[-2]
                address.pop(-1)
                address.pop(-1)
                data_dict['Area']=''.join(address)
                data_list.clear()
                
        for i in data_list:
            k=0
            for j in [*i]:
                if j in ['1','2','3','4','5','6','7','8','9','0']:
                    k=k+1
            if k>5:
                data_dict['State']=i.split()[0]
                data_dict['Pin_code']=i.split()[1]
                data_list.remove(i)
                
        if len(data_list)==3:
            data_dict['Company_name']=data_list[1]+' '+data_list[2]
            address= re.split(r',|;',data_list[0])
            for i in address:
                if i=='':
                    address.remove(i)
            data_dict['City']=address[-1]
            address.pop(-1)
            data_dict['Area']=''.join(address)
            
        if len(data_list)>3:
            data_dict['Area']=data_list[0]
            data_dict['City']=data_list[1]
            data_dict['Company_name']=data_list[2]+' '+data_list[3]
            
        verified_data=['uploaded_image']
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
                else:
                    st.warning("Data already present. Please click on 'View/Delete' button to update the data", icon= "🚨")
        
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
            sql=("select Image from business_card where Email_address= %s ")
            mycursor.execute(sql,[mail_input])
            for i in mycursor:
                fetched_image=i[0]
            with open('name','wb') as file:
                file.write(fetched_image)
            st.image(name,width=550)