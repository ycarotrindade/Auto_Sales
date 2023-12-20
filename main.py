import streamlit as st
import pandas as pd
import plotly.express as px
import os
import io

st.set_page_config(page_title='Auto Sales',page_icon=':bar_chart:',layout='wide')
st.title('Auto Sales Analysis')

df=pd.read_csv('Auto Sales data.csv')
col1,col2=st.columns((2))
df['ORDERDATE']=pd.to_datetime(df['ORDERDATE'])
startDate=pd.to_datetime(df['ORDERDATE'].min())
endDate=pd.to_datetime(df['ORDERDATE'].max())

with col1:
    date1=pd.to_datetime(st.date_input('Start Date',startDate))

with col2:
    date2=pd.to_datetime(st.date_input('End Date',endDate))

df=df[(df['ORDERDATE']>=date1)&(df['ORDERDATE']<=date2)].copy()

st.sidebar.header('Choose your filter:')
country=st.sidebar.multiselect('Pick your Country',df['COUNTRY'].unique())
if not country:
    df2=df.copy()
else:
    df2=df[df['COUNTRY'].isin(country)]

city=st.sidebar.multiselect('Choose Your City',df2['CITY'].unique())
if not city:
    df3=df2.copy()
else:
    df3=df2[df2['CITY'].isin(city)]
by_what=st.sidebar.radio(label='Choose the metric',options=['SALES','QUANTITY ORDERED'])

with col1:
    st.subheader('Dealsize Quantity')
    dealsize_df=df3['DEALSIZE'].value_counts()
    fig=px.pie(dealsize_df,names=dealsize_df.index,values=dealsize_df.values)
    st.plotly_chart(fig,True)
    
with col2:
    st.subheader('Status Quantity')
    status_df=df3['STATUS'].value_counts()
    fig=px.pie(status_df,names=status_df.index,values=status_df.values)
    st.plotly_chart(fig,True)
    
with col1:
    st.subheader(f'{by_what} By Country')
    country_sales_df=df3.groupby(by=['COUNTRY'],as_index=False)[f'{by_what}'.replace(' ','')].sum()
    st.bar_chart(country_sales_df,x='COUNTRY',y=f'{by_what}'.replace(' ',''))

with col2:
    st.subheader(f'{by_what} By City')
    city_sales_df=df3.groupby(by=['CITY'],as_index=False)[f'{by_what}'.replace(' ','')].sum()
    st.bar_chart(city_sales_df,x='CITY',y=f'{by_what}'.replace(' ',''))

cl1,cl2=st.columns(2)
with cl1:
    with st.expander('By Country Database'):
        if by_what=='SALES':
            country_sales_df['SALES']=country_sales_df['SALES'].map('${:.2f}'.format)
        else:
            country_sales_df[f'{by_what}'.replace(' ','')]=country_sales_df[f'{by_what}'.replace(' ','')]
        st.table(country_sales_df)
        output=io.BytesIO()
        writer=pd.ExcelWriter(output,engine='xlsxwriter')
        country_sales_df.to_excel(writer,index=False,sheet_name='sheet1')
        writer.close()
        data_bytes=output.getvalue()
        st.download_button(label='Download Table',data=data_bytes,file_name='country_df.xlsx')
with cl2:
    with st.expander('By City Sales'):
        if by_what=='SALES':
            city_sales_df['SALES']=city_sales_df['SALES'].map('${:.2f}'.format)
        else:
            city_sales_df[f'{by_what}'.replace(' ','')]=city_sales_df[f'{by_what}'.replace(' ','')]
        st.table(city_sales_df)
        output=io.BytesIO()
        writer=pd.ExcelWriter(output,engine='xlsxwriter')
        city_sales_df.to_excel(writer,index=False,sheet_name='sheet1')
        writer.close()
        data_bytes=output.getvalue()
        st.download_button(label='Download Table',data=data_bytes,file_name='city_df.xlsx')

df3['month_year']=df3['ORDERDATE'].dt.to_period('M')
st.subheader('Time Series Analysis')
linechart=pd.DataFrame(df3.groupby(df3['month_year'])[f'{by_what}'.replace(' ','')].sum()).reset_index()
linechart['month_year']=linechart['month_year'].dt.strftime('%Y:%b')
fig2=px.line(linechart,x='month_year',y=f'{by_what}'.replace(' ',''),labels={f'{by_what}'.replace(' ',''):'Amount'},height=500,width=1000,template='gridon')
st.plotly_chart(fig2,use_container_width=True)

with st.expander('Data of TimeSeries'):
    if by_what=='SALES':
        linechart['SALES']=linechart['SALES'].map('${:.2f}'.format)
    else:
        linechart[f'{by_what}'.replace(' ','')]=linechart[f'{by_what}'.replace(' ','')]
    st.table(linechart)
    output=io.BytesIO()
    writer=pd.ExcelWriter(output,engine='xlsxwriter')
    linechart.to_excel(writer,index=False,sheet_name='sheet1')
    writer.close()
    data_bytes=output.getvalue()
    st.download_button(label='Download Table',data=data_bytes,file_name='linechart.xlsx')

st.subheader('Product Line Quantity')
productline_df=df3['PRODUCTLINE'].value_counts()
fig=px.pie(productline_df,names=productline_df.index,values=productline_df.values)
st.plotly_chart(fig,True)

colu1,colu2=st.columns(2)
with colu1:
    with st.expander('Product Line chart'):
        productline=df3.groupby(by=['PRODUCTLINE'],as_index=False)[f'{by_what}'.replace(' ','')].sum()
        st.bar_chart(productline,x='PRODUCTLINE',y=f'{by_what}'.replace(' ',''))

with colu2:
    with st.expander('Product line Dataframe'):
        if by_what=='SALES':
            productline[f'{by_what}'.replace(' ','')]=productline[f'{by_what}'.replace(' ','')].map('${:.2f}'.format)
        else:
            productline[f'{by_what}'.replace(' ','')]=productline[f'{by_what}'.replace(' ','')]
        st.table(productline)
        output=io.BytesIO()
        writer=pd.ExcelWriter(output,engine='xlsxwriter')
        productline.to_excel(writer,index=False,sheet_name='sheet1')
        writer.close()
        data_bytes=output.getvalue()
        st.download_button(data=data_bytes,label='Download Data',file_name='productline.xlsx')

st.subheader('Advanced Search')
column1,column2,column3=st.columns(3)
df4=df3.copy()
df4=df4.drop(axis=1,columns=['month_year'])
df4['ORDERNUMBER']=df4['ORDERNUMBER'].astype(str)
with column1:
    ordernumber=st.number_input(placeholder='Type a number',step=1,format='%d',label='Order Number')
    prodline=st.selectbox(label='Product line',options=df4['PRODUCTLINE'].unique(),index=False)
if ordernumber:
    df4=df4[df4['ORDERNUMBER']==str(ordernumber)].copy()
if prodline:
    df4=df4[df4['PRODUCTLINE']==prodline]
with column2:
    linenumber=st.number_input(placeholder='Type a number',step=1,format='%d',label='Order Line Number')
    contactfirst=st.text_input(label='Contact First Name')
if linenumber:
    df4=df4[df['ORDERLINENUMBER']==linenumber].copy()
if contactfirst:
    df4=df4[df4['CONTACTFIRSTNAME']==contactfirst]
with column3:
    status=st.selectbox('Status',df4['STATUS'].unique(),index=False)
    contactlast=st.text_input(label='Contact Last Name')
if status:
    df4=df4[df4['STATUS']==status]
if contactlast:
    df4=df4[df4['CONTACTLASTNAME']==contactlast]
st.dataframe(data=df4,use_container_width=True)
outupt=io.BytesIO()
writer=pd.ExcelWriter(output,'xlsxwriter')
df4.to_excel(writer,index=False,sheet_name='sheet1')
writer.close()
data_bytes=output.getvalue()
st.download_button(label='Download Data',file_name='data.xlsx',data=data_bytes)