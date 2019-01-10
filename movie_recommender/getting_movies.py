import sqlite3

if __name__ == '__main__':
	conn = sqlite3.connect("movie_titles")
	c = conn.cursor()
	for name in c.execute("SELECT name FROM sqlite_master WHERE type='table';"):
		print name