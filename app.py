import streamlit as st
from streamlit_option_menu import option_menu
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import pandas as pd
import calendar
from datetime import datetime
import altair as alt
import plotly.express as px


#database related stuff
import pyrebase

firebaseConfig = {
    'apiKey': st.secrets["auth_token"],
    'authDomain': "track-bucks-264c5.firebaseapp.com",
    'projectId' : "track-bucks-264c5",
    'databaseURL': "https://track-bucks-264c5-default-rtdb.europe-west1.firebasedatabase.app/",
    'storageBucket': "track-bucks-264c5.appspot.com",
    'messagingSenderId': "401486775290",
    'appId': "1:401486775290:web:85bc51c8705c2a5af1da43",
    'measurementId': "G-GSJ7XQ516W"
  }

firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()

db = firebase.database()
storage = firebase.storage()


#page


categories = ['Shopping', 'Groceries', 'Dining out','Housing', 'Clothing','Health and Medicines','Transport', 'Entertainment', 'Gifts', 'Bills', 'Other']
currencies = ['INR' , 'USD']
page_title = "Track bucks"
page_icon = ":money_with_wings:"
layout = 'centered'

st.set_page_config(page_title = page_title, page_icon = page_icon, layout = layout)
st.sidebar.title(page_title + " " + page_icon)

choice = st.sidebar.selectbox('Login/Signup', ['Login', 'Sign up'])

email = st.sidebar.text_input('Email')
password = st.sidebar.text_input('Password',type = 'password')

if choice == 'Sign up':
        handle = st.sidebar.text_input('Handle:', value = 'Default');
        currency = st.sidebar.selectbox("Currency:", currencies, key = "currency")
        monthly_target = st.sidebar.number_input('Your monthly target expenditure : ', key = 'monthly_target');
        submit = st.sidebar.button('Sign up')
        if submit:
                user = auth.create_user_with_email_and_password(email, password)
                st.success('Your account is created suceesfully!')
                st.balloons()
                # Sign in
                user = auth.sign_in_with_email_and_password(email, password)
                db.child(user['localId']).child("Handle").set(handle)
                db.child(user['localId']).child("ID").set(user['localId'])
                db.child(user['localId']).child("Currency").set(currency)
                db.child(user['localId']).child("Monthly Target Expenditure").set(monthly_target)
                st.title('Welcome' + handle)
                st.info('Login via login drop down selection')

# Login Block
if choice == 'Login':
    login = st.sidebar.checkbox('Login')
    if login:
        user = auth.sign_in_with_email_and_password(email,password)
        
        st.write('<style>div.row-widget.stRadio > div{flex-direction:row;}</style>', unsafe_allow_html=True)
        selected = option_menu(menu_title=None,options=["Dashboard", "New Expense", "All Expenses"],icons=["bar-chart-fill", "pencil-fill","bi bi-bag-fill"],  orientation="horizontal")

        
        if selected == 'New Expense':
                with st.form("entry_form", clear_on_submit=True):
                        st.date_input('Date', key = 'date')

                        "---"

                        st.text_input('What product or Service are you paying for?', key = 'product_name')
                        st.number_input('Price', min_value = 0.0, step = 10.0, key = 'price')
                        st.selectbox('Category', categories, key = 'category')
                        comment = st.text_area("Comment", placeholder="Enter a comment here ...")

                        "---"
                        submitted = st.form_submit_button("Save Data")
                if submitted:
                        date = str(st.session_state["date"])
                        product_name = st.session_state["product_name"]
                        category = st.session_state["category"]
                        price = st.session_state["price"]
                        expense = {'Date': date, 'Product name': product_name, 'Category': category, 'Price': price}
                        expenses = db.child(user['localId']).child("Expenses").push(expense)
                        st.success("Data saved!")
        elif selected == "Dashboard":
                st.header('Your expense charts')

                res = db.child(user['localId']).child("Expenses").get()
                months = list(calendar.month_name[1:])
                expenses  = dict(zip(months, map(lambda x: 0, months)))
                category_expenses = dict(zip(categories, map(lambda x: 0, categories)))
                for expense in res.each():
                        el = dict(expense.val())
                        date_object = datetime.strptime(el["Date"], "%Y-%m-%d").date()
                        month_name = calendar.month_name[date_object.month]
                        expenses[month_name] = expenses[month_name] + el['Price']
                        cat = el['Category']
                        category_expenses[cat] = category_expenses[cat] + el['Price']
                d = {'Month': list(expenses.keys()), 'Expenditure' : list(expenses.values())}
                expense_df = pd.DataFrame(d)
                target =  db.child(user['localId']).child("Monthly Target Expenditure").get()
                target=target.val()
                line = pd.DataFrame({'Months': months, 'Target': target})
                line_plot = alt.Chart(line).mark_line(color= 'red').encode(x=alt.X('Months', sort  = None), y='Target').interactive()
                chart = alt.Chart(expense_df).mark_bar().encode(x=alt.X('Month', sort  = None), y='Expenditure').interactive()
                chart = chart + line_plot
                st.altair_chart(chart, theme = 'streamlit', use_container_width = True)
                
                cd =  {'category': categories, 'Expenditure':list(category_expenses.values())}
                category_expenses = pd.DataFrame(cd)
                fig = px.pie(category_expenses, values = 'Expenditure', names = 'category')
                st.plotly_chart(fig, use_container_width=True)
        elif selected == 'All Expenses':
                df = pd.DataFrame(columns = ['Date', 'Product name', 'Category', 'Price'])
                res = db.child(user['localId']).child("Expenses").get()
                for expense in res.each():
                        el = dict(expense.val())
                        el = pd.DataFrame([el])
                        df = pd.concat([df, el], ignore_index=True)
                
                st.markdown(df.style.hide(axis="index").to_html(), unsafe_allow_html=True)
                                



