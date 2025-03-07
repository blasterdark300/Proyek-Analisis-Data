import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import geopandas as gpd
import contextily as ctx
from PIL import Image
import requests
from io import BytesIO

# Base URL dari repository GitHub
base_url = "https://raw.githubusercontent.com/blasterdark300/Proyek-Analisis-Data/submission-akhir/E-Commerce%20Public%20Dataset/"

# Load dataset langsung dari GitHub
orders = pd.read_csv(base_url + "orders_dataset.csv")
items = pd.read_csv(base_url + "order_items_dataset.csv")
products = pd.read_csv(base_url + "products_dataset.csv")
payments = pd.read_csv(base_url + "order_payments_dataset.csv")
reviews = pd.read_csv(base_url + "order_reviews_dataset.csv")
customers = pd.read_csv(base_url + "customers_dataset.csv")
sellers = pd.read_csv(base_url + "sellers_dataset.csv")
geolocation = pd.read_csv(base_url + "geolocation_dataset.csv")
category = pd.read_csv(base_url + "product_category_name_translation.csv")

# Cek apakah data berhasil dimuat
print(orders.head())

# Load logo dari GitHub
logo_url = base_url + "logo.png"
response = requests.get(logo_url)

if response.status_code == 200:
    logo = Image.open(BytesIO(response.content))
    st.sidebar.image(logo, use_container_width=True)
else:
    st.sidebar.write("Gagal memuat logo.")

# Sidebar
st.sidebar.header("Filter Data")
date_range = st.sidebar.date_input("Pilih Rentang Tanggal", [])

# 1. Kategori produk dengan jumlah pesanan terbanyak
st.subheader("Kategori Produk dengan Pesanan Terbanyak")
product_orders = items.groupby("product_id")["order_id"].count().reset_index()
product_orders = product_orders.merge(products, on="product_id")
product_orders = product_orders.groupby("product_category_name")["order_id"].sum().reset_index()
product_orders = product_orders.sort_values(by="order_id", ascending=False).head(10)
fig, ax = plt.subplots()
ax.barh(product_orders["product_category_name"], product_orders["order_id"], color="teal")
ax.set_xlabel("Jumlah Pesanan")
ax.set_ylabel("Kategori Produk")
ax.set_title("10 Kategori Produk Terlaris")
ax.invert_yaxis()
st.pyplot(fig)

# 2. Rata-rata waktu pengiriman per negara bagian
st.subheader("Rata-rata Waktu Pengiriman per Negara Bagian")
orders['order_purchase_timestamp'] = pd.to_datetime(orders['order_purchase_timestamp'])
orders['order_delivered_customer_date'] = pd.to_datetime(orders['order_delivered_customer_date'])
orders['delivery_duration_days'] = (orders['order_delivered_customer_date'] - orders['order_purchase_timestamp']).dt.days
delivery_by_state = customers.merge(orders, on='customer_id').groupby("customer_state")["delivery_duration_days"].mean().reset_index()
fig, ax = plt.subplots()
ax.barh(delivery_by_state["customer_state"], delivery_by_state["delivery_duration_days"], color="salmon")
ax.set_xlabel("Rata-rata Waktu Pengiriman (Hari)")
ax.set_ylabel("Negara Bagian")
ax.set_title("Waktu Pengiriman per Negara Bagian")
ax.invert_yaxis()
st.pyplot(fig)

# 3. Metode pembayaran yang paling sering digunakan
st.subheader("Distribusi Metode Pembayaran")
payment_analysis = payments.groupby("payment_type")["order_id"].count().reset_index()
payment_analysis = payment_analysis.sort_values(by="order_id", ascending=False)
fig, ax = plt.subplots()
ax.bar(payment_analysis["payment_type"], payment_analysis["order_id"], color="royalblue")
ax.set_xlabel("Metode Pembayaran")
ax.set_ylabel("Jumlah Transaksi")
ax.set_title("Metode Pembayaran Terpopuler")
st.pyplot(fig)

# 4. Distribusi rating review dari pelanggan
st.subheader("Distribusi Rating Review")
fig, ax = plt.subplots()
sns.histplot(reviews["review_score"], bins=5, kde=True, color="orange", ax=ax)
ax.set_xlabel("Rating")
ax.set_ylabel("Jumlah Ulasan")
ax.set_title("Distribusi Rating dari Pelanggan")
st.pyplot(fig)

# 5. Pola pesanan per bulan
st.subheader("Pola Pesanan per Bulan")
orders["month_year"] = orders["order_purchase_timestamp"].dt.to_period("M")
order_trends = orders.groupby("month_year")["order_id"].count().reset_index()
fig, ax = plt.subplots()
ax.plot(order_trends["month_year"].astype(str), order_trends["order_id"], marker="o", linestyle="-", color="darkorange")
ax.set_title("Tren Pesanan per Bulan")
ax.set_xlabel("Bulan")
ax.set_ylabel("Jumlah Pesanan")
plt.xticks(rotation=45)
st.pyplot(fig)

# 6. Sebaran lokasi pelanggan
st.subheader("Sebaran Lokasi Pelanggan")
geolocation_sample = geolocation.sample(10000)
fig, ax = plt.subplots(figsize=(10, 10))
ax.scatter(geolocation_sample["geolocation_lng"], geolocation_sample["geolocation_lat"], s=0.5, alpha=0.5, color="blue")
ax.set_title("Sebaran Lokasi Pelanggan di Brasil")
plt.axis("off")
st.pyplot(fig)

# 7. Kategori produk dengan nilai pendapatan tertinggi
st.subheader("Kategori Produk dengan Pendapatan Tertinggi")
revenue_per_category = items.merge(products, on="product_id").groupby("product_category_name")["price"].sum().reset_index()
revenue_per_category = revenue_per_category.sort_values(by="price", ascending=False).head(10)
fig, ax = plt.subplots()
ax.barh(revenue_per_category["product_category_name"], revenue_per_category["price"], color="teal")
ax.set_xlabel("Total Pendapatan (R$)")
ax.set_ylabel("Kategori Produk")
ax.set_title("10 Kategori Produk dengan Pendapatan Tertinggi")
ax.invert_yaxis()
st.pyplot(fig)

st.write("Analisis ini memberikan wawasan tentang kategori produk terlaris, pola pesanan, metode pembayaran yang digunakan pelanggan, serta distribusi geografis pelanggan.")

# 8. Sebaran Lokasi Pelanggan di Brasil
st.subheader("Sebaran Lokasi Pelanggan di Brasil")
if "geolocation_lat" in geolocation.columns and "geolocation_lng" in geolocation.columns:
    gdf = gpd.GeoDataFrame(
        geolocation, 
        geometry=gpd.points_from_xy(geolocation.geolocation_lng, geolocation.geolocation_lat),
        crs="EPSG:4326"
    ).to_crs(epsg=3857)
    fig, ax = plt.subplots(figsize=(12, 10))
    gdf.plot(ax=ax, markersize=5, color="Blue", alpha=0.6)
    ctx.add_basemap(ax, source=ctx.providers.CartoDB.Positron)
    ax.set_title("Sebaran Lokasi Pelanggan di Brasil")
    ax.axis("off")
    st.pyplot(fig)
else:
    st.write("Kolom 'geolocation_lat' dan 'geolocation_lng' tidak ditemukan dalam dataset.")
