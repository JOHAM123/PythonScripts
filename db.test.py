import psycopg2


def initdb():
    conn = psycopg2.connect(host="localhost", database="db_name",
                                user="user", password="password")
    try:
        if conn is not None:
            print('Connection established to PostgreSQL.')
        else:
            print('Connection not established to PostgreSQL.')

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)

    finally:
        if conn is not None:
            conn.close()
            print('Finally, connection closed.')


db = initdb()
