import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.image as mpimg
import urllib
from PIL import Image

# Load dataset
df_path = "E-Commerce Public Dataset/df.csv"
geolocation_path = "E-Commerce Public Dataset/geolocation_dataset.csv"
logo_path = "E-Commerce Public Dataset/logo.png"

df = pd.read_csv(df_path)
geolocation = pd.read_csv(geolocation_path)

# Pastikan format tanggal benar
df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])
df['order_delivered_customer_date'] = pd.to_datetime(df['order_delivered_customer_date'])

# Load logo
try:
    logo = Image.open(logo_path)
    st.sidebar.image(logo, use_container_width=True)
except FileNotFoundError:
    st.sidebar.write("Gagal memuat logo. Pastikan file logo.png ada di dalam folder.")

# Sidebar filter dengan batasan tanggal
st.sidebar.header("Filter Data")

# Menentukan batasan tanggal dari dataset
min_date = df["order_purchase_timestamp"].min().date()
max_date = df["order_purchase_timestamp"].max().date()

# Menambahkan filter dengan batasan tanggal
date_range = st.sidebar.date_input("Pilih Rentang Tanggal", [min_date, max_date], min_value=min_date, max_value=max_date)

# Pastikan input tanggal valid
if len(date_range) == 2:
    start_date, end_date = date_range
    df_filtered = df[(df["order_purchase_timestamp"].dt.date >= start_date) & (df["order_purchase_timestamp"].dt.date <= end_date)]
else:
    df_filtered = df  # Jika tidak ada filter, gunakan semua data

# **3.1 Produk dengan jumlah penjualan terbanyak**
st.subheader("3.1 Produk Mana yang Memiliki Jumlah Penjualan Terbanyak?")
product_orders = df_filtered.groupby("product_category_name")["order_id"].count().reset_index()
product_orders = product_orders.sort_values(by="order_id", ascending=False).head(10)

fig, ax = plt.subplots()
ax.barh(product_orders["product_category_name"], product_orders["order_id"], color="teal")
ax.set_xlabel("Jumlah Pesanan")
ax.set_ylabel("Kategori Produk")
ax.set_title("10 Produk Terlaris")
ax.invert_yaxis()
st.pyplot(fig)

# **3.2 Kategori dengan revenue tertinggi**
st.subheader("3.2 Kategori Produk Mana yang Memberikan Pendapatan Tertinggi?")
revenue_per_category = df_filtered.groupby("product_category_name")["price"].sum().reset_index()
revenue_per_category = revenue_per_category.sort_values(by="price", ascending=False).head(10)

fig, ax = plt.subplots()
ax.barh(revenue_per_category["product_category_name"], revenue_per_category["price"], color="teal")
ax.set_xlabel("Total Pendapatan (R$)")
ax.set_ylabel("Kategori Produk")
ax.set_title("10 Kategori Produk dengan Revenue Tertinggi")
ax.invert_yaxis()
st.pyplot(fig)

# **3.3 Metode pembayaran yang paling banyak dipilih pelanggan**
st.subheader("3.3 Metode Pembayaran yang Paling Sering Digunakan?")
payment_counts = df_filtered["payment_type"].value_counts()

fig, ax = plt.subplots(figsize=(8, 5))
colors = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99']
payment_counts.plot(kind="pie", autopct='%1.1f%%', colors=colors, ax=ax)
ax.set_title("Distribusi Metode Pembayaran")
ax.set_ylabel("")
st.pyplot(fig)

# **3.4 Kota dengan transaksi terbanyak**
st.subheader("3.4 Kota Mana yang Memiliki Jumlah Pesanan Terbanyak?")
city_orders = df_filtered.groupby("customer_city")["order_id"].count().reset_index()
city_orders = city_orders.sort_values(by="order_id", ascending=False).head(10)

fig, ax = plt.subplots()
ax.barh(city_orders["customer_city"], city_orders["order_id"], color="purple")
ax.set_xlabel("Jumlah Transaksi")
ax.set_ylabel("Kota")
ax.set_title("10 Kota dengan Transaksi Terbanyak")
ax.invert_yaxis()
st.pyplot(fig)

# **3.5 Tren transaksi per bulan**
st.subheader("3.5 Kapan Waktu dengan Volume Transaksi Tertinggi?")
df_filtered["month_year"] = df_filtered["order_purchase_timestamp"].dt.to_period("M")
order_trends = df_filtered.groupby("month_year")["order_id"].count().reset_index()

fig, ax = plt.subplots()
ax.plot(order_trends["month_year"].astype(str), order_trends["order_id"], marker="o", linestyle="-", color="blue")
ax.set_title("Tren Pesanan per Bulan")
ax.set_xlabel("Bulan")
ax.set_ylabel("Jumlah Pesanan")
plt.xticks(rotation=45)
st.pyplot(fig)

# **3.6 Distribusi rating pelanggan**
st.subheader("3.6 Bagaimana Review Score Terdistribusi?")
review_counts = df_filtered["review_score"].value_counts().sort_index()

fig, ax = plt.subplots(figsize=(8,5))
review_counts.plot(kind="bar", color="orange", ax=ax)
ax.set_xlabel("Review Score")
ax.set_ylabel("Jumlah Review")
ax.set_title("Distribusi Review Score")
st.pyplot(fig)

# **3.7 Rata-rata waktu pengiriman**
st.subheader("3.7 Berapa Lama Waktu yang Dibutuhkan untuk Pengiriman?")
df_filtered['delivery_duration_days'] = (df_filtered['order_delivered_customer_date'] - df_filtered['order_purchase_timestamp']).dt.days
delivery_by_state = df_filtered.groupby("customer_state")["delivery_duration_days"].mean().reset_index()

fig, ax = plt.subplots()
ax.barh(delivery_by_state["customer_state"], delivery_by_state["delivery_duration_days"], color="salmon")
ax.set_xlabel("Rata-rata Waktu Pengiriman (Hari)")
ax.set_ylabel("Negara Bagian")
ax.set_title("Waktu Pengiriman per Negara Bagian")
ax.invert_yaxis()
st.pyplot(fig)

# **3.8 Sebaran lokasi pelanggan**
st.subheader("3.8 Bagaimana Sebaran Lokasi Pelanggan di Brasil?")

# Filter geolocation hanya untuk pelanggan yang ada di df_filtered
filtered_geolocation = geolocation[geolocation['geolocation_zip_code_prefix'].isin(df_filtered['customer_zip_code_prefix'])]

# Ambil sampel untuk ditampilkan agar tetap responsif
geolocation_sample = filtered_geolocation.sample(min(10000, len(filtered_geolocation)), random_state=42)

def plot_brazil_map(data):
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.scatter(data["geolocation_lng"], data["geolocation_lat"], s=2, alpha=0.7, color="blue")  # Titik lebih jelas
    
    # Gambar latar peta Brasil
    brazil_map_url = 'https://i.pinimg.com/originals/3a/0c/e1/3a0ce18b3c842748c255bc0aa445ad41.jpg'
    brazil = mpimg.imread(urllib.request.urlopen(brazil_map_url), 'jpg')
    ax.imshow(brazil, extent=[-73.98283055, -33.8, -33.75116944, 5.4], alpha=0.5)

    ax.set_title("Sebaran Lokasi Pelanggan di Brasil")
    plt.axis("off")
    return fig

fig = plot_brazil_map(geolocation_sample)
st.pyplot(fig)
