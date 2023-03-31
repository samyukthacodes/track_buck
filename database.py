import os
import streamlit as st
from deta import Deta
from dotenv import load_dotenv

load_dotenv(".env")
DETA_KEY = os.getenv("DETA_KEY")
deta = Deta(DETA_KEY)

db = deta.Base("tracebuckrecords")
def insert_record(currency, date, product_name, price, category, comment):
    return db.put({"currency": currency, "date" : date, "product_name":product_name, "price":price, "category": category, "comment":comment})


def fetch_all():
    """Returns a dict of all periods"""
    res = db.fetch()
    return res.items