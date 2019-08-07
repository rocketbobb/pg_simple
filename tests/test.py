import pg_simple
import sys
import datetime

connection_pool = pg_simple.config_pool(database='wms',
                                        host='localhost',
                                        port='54321',
                                        user='***',
                                        password='***',
                                        expiration=120)     # idle timeout = 120 seconds

db = pg_simple.PgSimple(connection_pool,
                        log=sys.stdout,
                        log_fmt=lambda x: '>> %s' % (x if isinstance(x, str) else x.query),
                        nt_cursor=True)

# dropping and creating tables
db.drop('books')

db.create('books',
          '''
"id" SERIAL NOT NULL,
"genre" VARCHAR(20) NOT NULL,
"name" VARCHAR(40) NOT NULL,
"price" MONEY NOT NULL,
"published" DATE NOT NULL,
"modified" TIMESTAMP(6) NOT NULL DEFAULT now()
'''
)

db.execute('''ALTER TABLE "books" ADD CONSTRAINT "books_pkey" PRIMARY KEY ("id")''')
db.commit()

# emptying a table or set of tables
#db.truncate('tbl1')
#db.truncate('tbl2, tbl3', restart_identity=True, cascade=True)
#db.commit()

# inserting rows
for i in range(1, 10):
    db.insert("books",
              {"genre": "fiction",
               "name": "Book Name vol. %d" % i,
               "price": 1.23 * i,
               "published": "%d-%d-1" % (2000 + i, i)})

db.commit()

# Updating rows
with pg_simple.PgSimple(connection_pool) as db1:
    db1.update('books',
               data={'name': 'An expensive book',
                     'price': 998.997,
                     'genre': 'non-fiction',
                     'modified': 'NOW()'},
               where=('published = %s', [datetime.date(2001, 1, 1)]))

    db1.commit()

# deleting rows
db.delete('books', where=('published >= %s', [datetime.date(2005, 1, 31)]))
db.commit()

# Inserting/updating/deleting rows with return value
row = db.insert("books",
                {"genre": "fiction",
                 "name": "Book with ID",
                 "price": 123.45,
                 "published": "1997-01-31"},
                returning='id')
print(row.id)

rows = db.update('books',
                 data={'name': 'Another expensive book',
                       'price': 500.50,
                       'modified': 'NOW()'},
                 where=('published = %s', [datetime.date(2006, 6, 1)]),
                 returning='modified')
print(rows)
#print(rows[0].modified)

rows = db.delete('books',
                 where=('published >= %s', [datetime.date(2005, 1, 31)]),
                 returning='name')
for r in rows:
    print(r.name)

#Fetching a single record
book = db.fetchone('books',
                   fields=['name', 'published'],
                   where=('published = %s', [datetime.date(2002, 2, 1)]))

print(book.name + ' was published on %s', book[1])

# Fetching multiple records
books = db.fetchall('books',
                    fields=['name AS n', 'genre AS g'],
                    where=('published BETWEEN %s AND %s', [datetime.date(2005, 2, 1), datetime.date(2009, 2, 1)]),
                    order=['published', 'DESC'],
                    limit=5,
                    offset=2)

for book in books:
    print(book.n + 'belongs to ' + book[1])

# Explicit database transaction management
with pg_simple.PgSimple(connection_pool) as _db:
    try:
        _db.execute("SELECT COUNT(*) FROM books")
        _db.commit()
    except:
        _db.rollback()

# Implicit database transaction management
with pg_simple.PgSimple(connection_pool) as _db:
    _db.execute("SELECT COUNT(*) FROM books")
    _db.commit()


# misc commands, exploring database
# raw SQL execution
db.execute('SELECT tablename FROM pg_tables WHERE schemaname=%s and tablename=%s', ['public', 'books'])

# misc commands, exploring
'''
db.execute("SELECT COUNT(*) AS tables \
FROM ( \
SELECT table_name FROM information_schema.tables WHERE table_schema='public' and table_type='BASE TABLE' \
) as summary;")
'''
