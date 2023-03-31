import streamlit as st
from streamlit_option_menu import option_menu
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import pandas as pd
import calendar
from datetime import datetime
import altair as alt
import database as db
import plotly.express as px

categories = ['Shopping', 'Groceries', 'Dining out','Housing', 'Transport', 'Entertainment', 'Gifts', 'Bills', 'Other']
currencies = ['INR' , 'USD']
page_title = "Track bucks"
page_icon = ":money_with_wings:"
layout = 'centered'

st.set_page_config(page_title = page_title, page_icon = page_icon, layout = layout)
st.title(page_title + " " + page_icon)
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)
selected = option_menu(
    menu_title=None,
    options=["Dashboard", "New expense"],
    icons=["bar-chart-fill", "pencil-fill"],  # https://icons.getbootstrap.com/
    orientation="horizontal",
)

years = [datetime.today().year - 1, datetime.today().year]
months = list(calendar.month_name[1:])

if selected == "New expense":
        with st.form("entry_form", clear_on_submit=True):
                currency = st.selectbox("Currency:", currencies, key = "currency")
                st.date_input('Date', key = 'date')

                "---"

                st.text_input('What product or Service are you paying for?', key = 'product_name')
                st.number_input('Price', min_value = 0.0, step = 10.0, key = 'price')
                st.selectbox('Category', categories, key = 'category')
                comment = st.text_area("Comment", placeholder="Enter a comment here ...")

                "---"
                submitted = st.form_submit_button("Save Data")

        if submitted:
                currency = st.session_state["currency"]
                date = str(st.session_state["date"])
                product_name = st.session_state["product_name"]
                category = st.session_state["category"]
                price = st.session_state["price"]
                db.insert_record(currency, date, product_name, price, category, comment)
                st.success("Data saved!")


elif selected == "Dashboard":
        st.header('Your expense charts')

        res = db.fetch_all()
        months = list(calendar.month_name[1:])
        expenses  = dict(zip(months, map(lambda x: 0, months)))
        category_expenses = dict(zip(categories, map(lambda x: 0, categories)))
        for el in res:
                date_object = datetime.strptime(el["date"], "%Y-%m-%d").date()
                month_name = calendar.month_name[date_object.month]
                expenses[month_name] = expenses[month_name] + el['price']
                cat = el['category']
                category_expenses[cat] = category_expenses[cat] + el['price']
        d = {'Month': list(expenses.keys()), 'Expenditure' : list(expenses.values())}
        expense_df = pd.DataFrame(d)
        chart = alt.Chart(expense_df).mark_bar().encode(x=alt.X('Month', sort    = None), y='Expenditure').interactive()
        st.altair_chart(chart, theme = 'streamlit', use_container_width = True)
        
        cd =  {'category': categories, 'Expenditure':list(category_expenses.values())}
        category_expenses = pd.DataFrame(cd)
        fig = px.pie(category_expenses, values = 'Expenditure', names = 'category')
        st.plotly_chart(fig, use_container_width=True)
