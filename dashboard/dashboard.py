import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import geopandas as gpd
import contextily as ctx
import matplotlib.image as mpimg
import urllib
from PIL import Image
import requests
from io import BytesIO

# Path ke dataset
df_path = "E-Commerce Public Dataset/df.csv"
geolocation_path = "E-Commerce Public Dataset/geolocation_dataset.csv"
logo_path = "E-Commerce Public Dataset/logo.png"

# Load dataset
df = pd.read_csv(df_path)
geolocation = pd.read_csv(geolocation_path)

# Load logo
try:
    logo = Image.open(logo_path)
    st.sidebar.image(logo, use_container_width=True)
except FileNotFoundError:
    st.sidebar.write("Gagal memuat logo. Pastikan file logo.png ada di dalam folder.")
    
    # Pastikan format tanggal benar
df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])
df['order_delivered_customer_date'] = pd.to_datetime(df['order_delivered_customer_date'])

# Sidebar filter
st.sidebar.header("Filter Data")
date_range = st.sidebar.date_input("Pilih Rentang Tanggal", [])

# 3.1 Produk mana yang memiliki jumlah penjualan terbanyak?
st.subheader("3.1 Produk Mana yang Memiliki Jumlah Penjualan Terbanyak?")
product_orders = df.groupby("product_category_name")["order_id"].count().reset_index()
product_orders = product_orders.sort_values(by="order_id", ascending=False).head(10)

fig, ax = plt.subplots()
ax.barh(product_orders["product_category_name"], product_orders["order_id"], color="teal")
ax.set_xlabel("Jumlah Pesanan")
ax.set_ylabel("Kategori Produk")
ax.set_title("10 Produk Terlaris")
ax.invert_yaxis()
st.pyplot(fig)

# 3.2 Kategori produk apa yang memiliki revenue tertinggi?
st.subheader("3.2 Kategori Produk Mana yang Memberikan Pendapatan Tertinggi?")
revenue_per_category = df.groupby("product_category_name")["price"].sum().reset_index()
revenue_per_category = revenue_per_category.sort_values(by="price", ascending=False).head(10)

fig, ax = plt.subplots()
ax.barh(revenue_per_category["product_category_name"], revenue_per_category["price"], color="teal")
ax.set_xlabel("Total Pendapatan (R$)")
ax.set_ylabel("Kategori Produk")
ax.set_title("10 Kategori Produk dengan Revenue Tertinggi")
ax.invert_yaxis()
st.pyplot(fig)

# 3.3 Metode pembayaran mana yang paling banyak dipilih pelanggan?
st.subheader("3.3 Metode Pembayaran yang Paling Sering Digunakan?")

# Hitung jumlah transaksi per metode pembayaran
payment_counts = df["payment_type"].value_counts()

# Visualisasi Pie Chart
fig, ax = plt.subplots(figsize=(8, 5))
colors = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99']
payment_counts.plot(kind="pie", autopct='%1.1f%%', colors=colors, ax=ax)
ax.set_title("Distribusi Metode Pembayaran")
ax.set_ylabel("")  # Menghapus label y agar lebih rapi
# Tampilkan di Streamlit
st.pyplot(fig)

# 3.4 Kota mana yang memiliki transaksi terbanyak?
st.subheader("3.4 Kota Mana yang Memiliki Jumlah Pesanan Terbanyak?")
city_orders = df.groupby("customer_city")["order_id"].count().reset_index()
city_orders = city_orders.sort_values(by="order_id", ascending=False).head(10)

fig, ax = plt.subplots()
ax.barh(city_orders["customer_city"], city_orders["order_id"], color="purple")
ax.set_xlabel("Jumlah Transaksi")
ax.set_ylabel("Kota")
ax.set_title("10 Kota dengan Transaksi Terbanyak")
ax.invert_yaxis()
st.pyplot(fig)

# 3.5 Bulan kapan yang memiliki transaksi paling banyak?
st.subheader("3.5 Kapan Waktu dengan Volume Transaksi Tertinggi?")
df["month_year"] = df["order_purchase_timestamp"].dt.to_period("M")
order_trends = df.groupby("month_year")["order_id"].count().reset_index()

fig, ax = plt.subplots()
ax.plot(order_trends["month_year"].astype(str), order_trends["order_id"], marker="o", linestyle="-", color="blue")
ax.set_title("Tren Pesanan per Bulan")
ax.set_xlabel("Bulan")
ax.set_ylabel("Jumlah Pesanan")
plt.xticks(rotation=45)
st.pyplot(fig)

# 3.6 Seberapa puas pelanggan terhadap produk yang dibeli (rating)?
st.subheader("3.6 Bagaimana Review Score Terdistribusi?")
# Hitung jumlah review per skor
review_counts = df["review_score"].value_counts().sort_index()

# Visualisasi
fig, ax = plt.subplots(figsize=(8,5))
review_counts.plot(kind="bar", color="orange", ax=ax)  # Gunakan plot bar agar sama dengan gambar
ax.set_xlabel("Review Score")
ax.set_ylabel("Jumlah Review")
ax.set_title("Distribusi Review Score")

# Tampilkan di Streamlit
st.pyplot(fig)

# 3.7 Berapa rata-rata waktu pengiriman dari pembelian hingga diterima pelanggan?
st.subheader("3.7 Berapa Lama Waktu yang Dibutuhkan untuk Pengiriman?")
df['delivery_duration_days'] = (df['order_delivered_customer_date'] - df['order_purchase_timestamp']).dt.days
delivery_by_state = df.groupby("customer_state")["delivery_duration_days"].mean().reset_index()

fig, ax = plt.subplots()
ax.barh(delivery_by_state["customer_state"], delivery_by_state["delivery_duration_days"], color="salmon")
ax.set_xlabel("Rata-rata Waktu Pengiriman (Hari)")
ax.set_ylabel("Negara Bagian")
ax.set_title("Waktu Pengiriman per Negara Bagian")
ax.invert_yaxis()
st.pyplot(fig)

# 3.8 Bagaimana distribusi geografis pelanggan di Brasil berdasarkan kode pos?
st.subheader("3.8 Bagaimana Sebaran Lokasi Pelanggan di Brasil?")
# Ambil sampel untuk performa lebih baik
geolocation_sample = geolocation.sample(10000, random_state=42)

# Plot peta dengan latar belakang Brasil
def plot_brazil_map(data):
    fig, ax = plt.subplots(figsize=(10, 10))
    
    # Scatter plot titik lokasi
    ax.scatter(
        data["geolocation_lng"], 
        data["geolocation_lat"], 
        s=0.5, 
        alpha=0.5, 
        color="blue"
    )

    # Tambahkan latar belakang peta Brasil
    brazil_map_url = 'https://i.pinimg.com/originals/3a/0c/e1/3a0ce18b3c842748c255bc0aa445ad41.jpg'
    brazil = mpimg.imread(urllib.request.urlopen(brazil_map_url), 'jpg')
    ax.imshow(brazil, extent=[-73.98283055, -33.8, -33.75116944, 5.4], alpha=0.5)

    ax.set_title("Sebaran Lokasi Pelanggan di Brasil")
    plt.axis("off")

    return fig

# Streamlit UI
fig = plot_brazil_map(geolocation_sample)
st.pyplot(fig)