# Capstone Project API
Capstone project API sebagai tugas dalam training Python for Data Analysis dari Algoritma

Untuk membuka halaman menggunakan URL : https://hidayat-capstone-api.herokuapp.com

## Static Endpoints
- /, method = GET. Merupakan base endpoint, ucapan selamat datang.
- /docs, method = GET. Dokumentasi tentang penggunaan API.
- /data/get/catalog , method = GET. Untuk mendapatkan seluruh daftar lagu yang tersedia.
- /data/get/top10_songs , method = GET. Untuk mendapatkan daftar 10 lagu dengan penjualan terbanyak.
/data/get/top10_artists , method = GET. Untuk mendapatkan daftar 10 penyanyi dengan penjualan lagu terbanyak.

## Dinamic Endpoints
- /data/get/penjualan , method = GET. Untuk menampilkan seluruh data penjualan.

Filter yang dapat digunakan:
* year : memfilter data penjualan berdasarkan tahun penjualan, contoh: /data/get/penjualan?year=2012
* day : memfilter data penjualan berdasarkan nama hari (in english), contoh: /data/get/penjualan?day=Wednesday
* country : memfilter data penjualan berdasarkan negara, contoh: /data/get/penjualan?country=Germany
* genre : memfilter data penjualan berdasarkan genre musik, contoh: /data/get/penjualan?genre=Rock
* col : memfilter kolom yang ingin ditampilkan, contoh: /data/get/penjualan?col=[Song,Artist,Quantity]
* Untuk mengkombinasikan filter dapat digunakan tanda &, contoh: /data/get/penjualan?year=2012&genre=Rock
