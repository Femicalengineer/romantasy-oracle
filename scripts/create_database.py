import sqlite3
import pandas as pd

# Connect to database - creates the file if it doesn't exist
conn = sqlite3.connect("db/romantasy_oracle.db")
cursor = conn.cursor()

# --- TABLE 1: books ---
# Core information about each book
cursor.execute("""
CREATE TABLE IF NOT EXISTS books (
    book_id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    author TEXT NOT NULL,
    series TEXT,
    series_position INTEGER,
    genre TEXT,
    avg_rating REAL,
    page_count INTEGER,
    rep TEXT,
    format TEXT,
    owned BOOLEAN
)
""")

# --- TABLE 2: my_readings ---
# Your personal relationship with each book
# Separated from books because YOU might reread a book
cursor.execute("""
CREATE TABLE IF NOT EXISTS my_readings (
    reading_id INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id INTEGER NOT NULL,
    my_rating INTEGER,
    date_read DATE,
    spice_level INTEGER,
    notes TEXT,
    FOREIGN KEY (book_id) REFERENCES books(book_id)
)
""")

# --- TABLE 3: tropes ---
# Lookup table of romantasy tropes
cursor.execute("""
CREATE TABLE IF NOT EXISTS tropes (
    trope_id INTEGER PRIMARY KEY AUTOINCREMENT,
    trope_name TEXT NOT NULL UNIQUE,
    description TEXT
)
""")

# --- TABLE 4: book_tropes ---
# Links books to tropes - one book can have many tropes
cursor.execute("""
CREATE TABLE IF NOT EXISTS book_tropes (
    book_id INTEGER NOT NULL,
    trope_id INTEGER NOT NULL,
    PRIMARY KEY (book_id, trope_id),
    FOREIGN KEY (book_id) REFERENCES books(book_id),
    FOREIGN KEY (trope_id) REFERENCES tropes(trope_id)
)
""")

print("✅ Tables created successfully")

# --- LOAD DATA from sample_books.csv ---
df = pd.read_csv("data/sample_books.csv")

# Load books table
books_df = df[[
    "book_id", "title", "author", "series", "series_position",
    "genre", "avg_rating", "page_count", "rep", "format", "owned"
]]
books_df.to_sql("books", conn, if_exists="replace", index=False)
print(f"✅ Loaded {len(books_df)} books into books table")

# Load my_readings table
readings_df = df[["book_id", "my_rating", "date_read", "spice_level", "notes"]].copy()
readings_df["reading_id"] = range(1, len(readings_df) + 1)
readings_df.to_sql("my_readings", conn, if_exists="replace", index=False)
print(f"✅ Loaded {len(readings_df)} readings into my_readings table")

# --- SEED TROPES ---
tropes = [
    ("Enemies to Lovers", "protagonists start as enemies and fall in love"),
    ("Slow Burn", "romantic tension builds over a long time"),
    ("Fae Love Interest", "the love interest is fae"),
    ("Morally Grey LI", "love interest has questionable morals"),
    ("Chosen One", "protagonist is destined for greatness"),
    ("Found Family", "characters form a family-like bond"),
    ("Forced Proximity", "characters are forced to spend time together"),
    ("Bully Romance", "love interest starts as a bully"),
    ("Power Couple", "both protagonists are powerful"),
    ("Hurt Comfort", "one character comforts another through pain"),
    ("Reverse Harem", "one protagonist with multiple love interests"),
    ("Second Chance", "former lovers reunite"),
    ("Forbidden Love", "romance is forbidden by society or circumstance"),
    ("Instalove", "characters fall in love very quickly"),
]

cursor.executemany("""
    INSERT OR IGNORE INTO tropes (trope_name, description) VALUES (?, ?)
""", tropes)
print(f"✅ Loaded {len(tropes)} tropes into tropes table")

# --- SEED BOOK TROPES ---
book_tropes = [
    # ACOTAR - enemies to lovers, fae LI, slow burn
    (1, 1), (1, 3), (1, 7),
    # ACOMAF - morally grey LI, slow burn, forbidden love
    (2, 2), (2, 4), (2, 13),
    # ACOWAF - power couple, found family
    (3, 6), (3, 10),
    # ACOSF - enemies to lovers, bully romance, hurt comfort
    (5, 1), (5, 8), (5, 10),
    # Throne of Glass - chosen one, slow burn
    (6, 5), (6, 2),
    # Heir of Fire - forced proximity, morally grey LI
    (8, 7), (8, 4),
    # Crescent City - forbidden love, power couple
    (13, 13), (13, 10),
    # Zodiac Academy - bully romance, forced proximity, reverse harem
    (17, 8), (17, 7), (17, 11),
    (18, 8), (18, 4),
    (19, 8), (19, 13),
    (20, 2), (20, 13),
]

cursor.executemany("""
    INSERT OR IGNORE INTO book_tropes (book_id, trope_id) VALUES (?, ?)
""", book_tropes)
print(f"✅ Loaded {len(book_tropes)} book-trope relationships")

conn.commit()
conn.close()
print("\n🔮 Romantasy Oracle database is ready!")
