import unittest

from pymysqlpool.dbpool import DBPool


class TestPYMysqlPool(unittest.TestCase):
    def setUp(self) -> None:
        self.host = "192.168.12.86"
        self.port = 30000
        self.user = "root"
        self.password = "introcks1234"
        self.database = "vesion_book_console"

    def test_create_connection(self):
        pool = DBPool(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            database=self.database,
        )
        self.assertTrue(hasattr(pool, '_idle_cache'))
        self.assertEqual(len(pool._idle_cache), 0)
        con = pool.connect()
        self.assertEqual(len(pool._idle_cache), 0)
        self.assertTrue(hasattr(con, '_set_session_sql'))
        self.assertIsNone(con._set_session_sql)
        con.close()
        self.assertEqual(len(pool._idle_cache), 1)
        con_pop = pool._idle_cache[0]
        db = pool.connect()
        self.assertEqual(len(pool._idle_cache), 0)
        self.assertTrue(hasattr(db, '_work_con'))
        self.assertEqual(db._work_con, con_pop._work_con)
        self.assertTrue(hasattr(db, 'cursor'))
        self.assertTrue(hasattr(db, '_work_con'))
        db_con = db._work_con
        print(db_con.__dict__)
        self.assertTrue(hasattr(db_con, 'db'))
        self.assertEqual(db_con.db, b'vesion_book_console')
        self.assertTrue(hasattr(db_con, 'user'))
        self.assertEqual(db_con.user, b'root')
        cursor = db.cursor()
        cursor.execute('select 1')
        r = cursor.fetchone()
        print(r[0])
        cursor.close()
        self.assertEqual(r[0], 1)
        db.close()
        self.assertEqual(len(pool._idle_cache), 1)

        db = pool.connect()
        self.assertEqual(len(pool._idle_cache), 0)
        db.close()
        self.assertEqual(len(pool._idle_cache), 1)
        db = pool.connect()
        self.assertEqual(len(pool._idle_cache), 0)
        db.close()
        self.assertEqual(len(pool._idle_cache), 1)


if __name__ == '__main__':
    unittest.main()
