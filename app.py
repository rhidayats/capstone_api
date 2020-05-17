import pandas as pd
from flask import Flask, request

import sqlite3
conn = sqlite3.connect("data/chinook.db", check_same_thread=False)

invoices = pd.read_sql_query('''SELECT a.TrackId,a.Name as Song,e.Name as Artist,b.Title as Album,c.Name as Media,d.Name as Genre,
                             a.Composer,a.UnitPrice,g.CustomerId,h.FirstName,h.LastName,f.Quantity,g.InvoiceDate,h.City,h.Country
                             FROM tracks a
                             LEFT JOIN albums b ON a.AlbumId = b.AlbumId
                             LEFT JOIN media_types c ON a.MediaTypeId = c.MediaTypeId
                             LEFT JOIN genres d ON a.GenreId = d.GenreId
                             LEFT JOIN artists e ON b.ArtistId = e.ArtistId
                             LEFT JOIN invoice_items f ON a.TrackId = f.TrackId
                             LEFT JOIN invoices g ON f.InvoiceId = g.InvoiceId
                             LEFT JOIN customers h ON g.CustomerId = h.CustomerId''', conn, parse_dates='InvoiceDate')

# mengubah tipe data                                
invoices.Media = invoices.Media.astype('category')
invoices.Genre = invoices.Genre.astype('category')
invoices.City = invoices.City.astype('category')
invoices.Country = invoices.Country.astype('category')

invoices["CustomerName"] = invoices["FirstName"]+" "+invoices["LastName"]

# mengisi nilai kosong pada dataframe
invoices["Composer"].fillna('Unknown',inplace=True)
invoices["Quantity"].fillna(0,inplace=True)

# menambahkan tahun dan hari
invoices["InvoiceYear"] = invoices["InvoiceDate"].dt.year
invoices["Weekday"] = invoices["InvoiceDate"].dt.day_name()

# mengambil daftar katalog lagu
catalog = invoices[["TrackId","Song","Album","Media","Genre","UnitPrice"]]
# menghilangkan duplikat
catalog.drop_duplicates(keep='first',inplace=True)

# 10 lagu dengan penjualan terbesar
top10_songs = invoices[['Song','Artist','Quantity']].groupby(['Song','Artist']).sum().sort_values(by='Quantity', ascending=False).head(10)
top10_songs = top10_songs.stack().unstack(level=1).unstack(level=0).melt(value_name='Quantity').dropna()

# 10 artist dengan penjualan terbesar
top10_artists = invoices[['Artist','Quantity']].groupby(['Artist']).sum().sort_values(by='Quantity', ascending=False).head(10)
top10_artists = top10_artists.stack().unstack(level=0).melt(value_name='Quantity')

# mendapatkan hanya data penjualan
data_penjualan = invoices.dropna()

app = Flask(__name__) 

@app.route('/')
def welcome():
    return '''<h1> Selamat Datang </h1>'''

@app.route("/docs")
def documentation():
    return '''
        <h1> Documentation </h1>
        <h2> Static Endpoints </h2>
        <ol>
            <li>
                <p> / , method = GET </p>
                <p> Base Endpoint, ucapan selamat datang. </p>
            </li>
            <li>
                <p> /data/get/catalog , method = GET </p>
                <p> Mendapatkan seluruh daftar lagu yang tersedia. </p>
            </li>
            <li>
                <p> /data/get/top10_songs , method = GET </p>
                <p> Mendapatkan daftar 10 lagu dengan penjualan terbanyak. </p>
            </li>
            <li>
                <p> /data/get/top10_artists , method = GET </p>
                <p> Mendapatkan daftar 10 penyanyi dengan penjualan lagu terbanyak. </p>
            </li>
        </ol>
         
        <h2> Dynamic Endpoints </h2>
        <ol start = "5">
            <li>
                <p> /data/get/penjualan , method = GET </p>
                <p> Menampilkan seluruh data penjualan </p>
                <p> Filter yang dapat digunakan : </p>
                <ul style="list-style-type:disc;">
                    <li> year : memfilter data penjualan berdasarkan tahun penjualan, contoh:
                        /data/get/penjualan?year=2012</li>
                    <li> day : memfilter data penjualan berdasarkan nama hari (in english), contoh:
                        /data/get/penjualan?day=Wednesday</li>
                    <li> country : memfilter data penjualan berdasarkan negara, contoh:
                        /data/get/penjualan?country=Germany</li>
                    <li> genre : memfilter data penjualan berdasarkan genre musik, contoh:
                        /data/get/penjualan?genre=Rock</li>
                    <li> col : memfilter kolom yang ingin ditampilkan, contoh:
                        /data/get/penjualan?col=[Song,Artist,Quantity]</li>
                </ul>
                <p> Untuk mengkombinasikan filter dapat digunakan tanda &amp, contoh:
                    /data/get/penjualan?year=2012&genre=Rock </p>
            </li>
        </ol>'''

# mendapatkan keseluruhan daftar lagu
@app.route('/data/get/catalog', methods=['GET']) 
def get_catalog(): 
    return (catalog.to_json())

# mendapatkan top 10 lagu terlaris
@app.route('/data/get/top10_songs', methods=['GET']) 
def get_top10_songs(): 
    return (top10_songs.to_json())

# mendapatkan top 10 artist terlaris
@app.route('/data/get/top10_artists', methods=['GET']) 
def get_top10_artist(): 
    return (top10_artists.to_json())

# mendapatkan data dengan filter
@app.route('/data/get/penjualan', methods=['GET']) 
def penjualan():
    params = request.args
    
    year = params.get('year')
    day = params.get('day')
    country = params.get('country')
    genre = params.get('genre')
    col = params.get('col')
    
    column = []
    equal = []
    condition = []
    if (year==None) & (day==None) & (country==None) & (genre==None):
        return (data_penjualan.to_json())
    if year:
        column.append('InvoiceYear')
        equal.append('==')
        condition.append(int(year))
    if day:
        column.append('Weekday')
        equal.append('==')
        condition.append(day)
    if country:
        column.append('Country')
        equal.append('==')
        condition.append(country)
    if genre:
        column.append('Genre')
        equal.append('==')
        condition.append(genre)
    
    data_filter = ' & '.join(f'{i} {j} {repr(k)}' for i, j, k in zip(column, equal, condition))
    
    if col==None:     
        return (data_penjualan.query(data_filter).to_json())
    else:
        cols = col[1:-1].split(',')
        return (data_penjualan.query(data_filter)[cols].to_json())

if __name__ == '__main__':
    app.run(debug=True, port=5000) 