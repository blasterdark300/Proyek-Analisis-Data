import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.image as mpimg
import urllib
from PIL import Image
import requests
from io import BytesIO

# Base URL dari repository GitHub
base_url = "https://raw.githubusercontent.com/blasterdark300/Proyek-Analisis-Data/submission-akhir/E-Commerce%20Public%20Dataset/dashboard/E-Commerce Public Dataset/"

# Path ke dataset di GitHub
df_url = base_url + "df.csv"
geolocation_url = base_url + "geolocation_dataset.csv"
logo_url = base_url + "logo.png"

# Load dataset dari GitHub
df = pd.read_csv(df_url)
geolocation = pd.read_csv(geolocation_url)

# Load logo dari GitHub
try:
    response = requests.get(logo_url)
    response.raise_for_status()
    logo = Image.open(BytesIO(response.content))
    st.sidebar.image(logo, use_container_width=True)
except requests.exceptions.RequestException:
    st.sidebar.write("Gagal memuat logo. Pastikan file logo.png tersedia di GitHub.")

# Pastikan format tanggal benar
df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])
df['order_delivered_customer_date'] = pd.to_datetime(df['order_delivered_customer_date'])

# Sidebar filter
st.sidebar.header("Filter Data")
date_range = st.sidebar.date_input("Pilih Rentang Tanggal", [])

# 3.8 Bagaimana Sebaran Lokasi Pelanggan di Brasil?
st.subheader("3.8 Bagaimana Sebaran Lokasi Pelanggan di Brasil?")

# Ambil sampel untuk performa lebih baik
geolocation_sample = geolocation.sample(10000, random_state=42)

# Fungsi untuk plot peta Brasil
def plot_brazil_map(data):
    fig, ax = plt.subplots(figsize=(10, 10))

    # Scatter plot titik lokasi pelanggan
    ax.scatter(
        data["geolocation_lng"], 
        data["geolocation_lat"], 
        s=0.5, 
        alpha=0.5, 
        color="blue"
    )

    # Tambahkan latar belakang peta Brasil
    brazil_map_url = 'https://i.pinimg.com/originals/3a/0c/e1/3a0ce18b3c842748c255bc0aa445ad41.jpg'
    brazil = mpimg.imread(urllib.request.urlopen(brazil_map_url))
    ax.imshow(brazil, extent=[-73.98283055, -33.8, -33.75116944, 5.4], alpha=0.5)

    ax.set_title("Sebaran Lokasi Pelanggan di Brasil")
    plt.axis("off")

    return fig

# Tampilkan peta di Streamlit
fig = plot_brazil_map(geolocation_sample)
st.pyplot(fig)
