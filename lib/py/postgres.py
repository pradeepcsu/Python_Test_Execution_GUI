import os
import tkMessageBox
import sys
try:
    import psycopg2
    from psycopg2 import IntegrityError, ProgrammingError, InternalError
except ImportError as e:
    tkMessageBox.showerror('Error', 'psycopg2 is not installed!')
    sys.exit(1)


_host = '90tvmcjnkd.ssfcuad.ssfcu.org'
_dbname = 'autotest'
_user = 'autotest'
_password = 'autotest'


def connect_db(host=_host, dbname=_dbname, user=_user, password=_password):
    try:
        conn_str = "host={} dbname={} user={} password={}".format(host, dbname, user, password)
        conn = psycopg2.connect(conn_str)
    except psycopg2.OperationalError as e:
        tkMessageBox.showerror('Error', 'An error occurred while connecting to the database:\n\n{}'.format(e))
        return
    return conn


def save_batch_vars(aut, suite, test, **vars):
    conn = connect_db()
    cur = conn.cursor()
    for k, v in vars.iteritems():
        try:
            q = 'insert into host.batch(aut,suite,test,key,value) values (%s,%s,%s,%s,%s)'
            cur.execute(q, (aut, suite, test, k, str(v)))
            conn.commit()
        except IntegrityError:
            conn.rollback()
            q = 'update host.batch set value=%s where aut=%s and suite=%s and test=%s and key=%s'
            cur.execute(q, (str(v), aut, suite, test, k))
            conn.commit()


def load_batch_vars(aut, suite, test):
    conn = connect_db()
    q = 'select key, value from host.batch where aut=%s and suite=%s and test=%s'
    cur = conn.cursor()
    cur.execute(q, (aut, suite, test))
    results = cur.fetchall()
    print('results: {}'.format(results))
    return results


class DatabaseConnBase:

    def __init__(self):
        self.conn = None

    def connect(self, host=_host, dbname=_dbname, user=_user, password=_password):
        try:
            conn_str = "host={} dbname={} user={} password={}".format(host, dbname, user, password)
            self.conn = psycopg2.connect(conn_str)
        except psycopg2.OperationalError as e:
            tkMessageBox.showerror('Error', 'An error occurred while connecting to the database:\n\n{}'.format(e))
            return False
        return True

    def disconnect(self):
        if self.conn:
            self.conn.close()

