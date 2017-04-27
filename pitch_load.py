from urllib.request import Request, urlopen
from urllib.parse import urlparse
from urllib.parse import urljoin
from bs4 import BeautifulSoup

import urllib.error
import sqlite3
import json
import time
import ssl


#connect/create database
conn = sqlite3.connect('pitchscraper.sqlite')
#create way to talk to database
cur = conn.cursor()

print('creating tables in database...')
#create table
cur.execute('''
	CREATE TABLE IF NOT EXISTS Master (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE, album_title TEXT UNIQUE, artist_name TEXT, score TEXT )''')

cur.execute('''
	CREATE TABLE IF NOT EXISTS Albums (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE, album_title TEXT UNIQUE)''')

cur.execute('''
	CREATE TABLE IF NOT EXISTS Artists (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE, artist_name TEXT UNIQUE)''')

cur.execute('''
	CREATE TABLE IF NOT EXISTS Ratings (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE, score TEXT)''')

count = 0
while count < 20:
	count = count+ 1

	print('connecting to pitchfork page' ,count)
	page = str(count)
	firsturl = 'http://pitchfork.com/reviews/albums/?page='
	#open and read page
	req = Request(firsturl+page, headers={'User-Agent': 'Mozilla/5.0'})
	pitchpage = urlopen(req).read()


	#parse with beautiful soup
	soup = BeautifulSoup(pitchpage, "lxml")
	albums = soup('h2')
	artists = soup.find_all(attrs={"class" : "artist-list"})
	links = soup.find_all(attrs={"class" : "album-link"})
	rating = soup.find_all(attrs={"class" : "score"})

	print('finding albums from page', count)
	for tag in albums:
		for album in tag:
			print(album)
			cur.execute('INSERT OR IGNORE INTO Albums (album_title) VALUES (?)', (album, ))			
			
	print('finding artists from page', count)	
	for artist in artists:
		print(artist.string)
		artist = artist.string	
		cur.execute('INSERT OR IGNORE INTO Artists(artist_name) VALUES (?)', (artist, ))		



	print('finding ratings from page', count)
	#extract URL
	for line in links:

		album_url = (line.get('href'))

		#open and read page
		req2 = Request('http://pitchfork.com' + album_url, headers={'User-Agent': 'Mozilla/5.0'})
		pitchpage2 = urlopen(req2).read()
		soup2 = BeautifulSoup(pitchpage2, "lxml")

		#extract rating
		rating = soup2.find("span", {"class": "score"})
		ratingstring = rating.string
		cur.execute('INSERT OR IGNORE INTO Ratings (score) VALUES (?)', (ratingstring, ))

		
	cur.execute('''SELECT Albums.album_title, Artists.artist_name, Ratings.score FROM Albums JOIN Artists ON Albums.id = Artists.id JOIN Ratings ON Albums.id = Ratings.id ''')
	row  = cur.fetchall()
	print(row)
	for couple in row:
		cur.execute('''INSERT OR IGNORE INTO Master (album_title, artist_name, score) VALUES (?, ?, ?)''', (couple[0], couple[1], couple[2]))


	print()
	conn.commit()

	#spider 








