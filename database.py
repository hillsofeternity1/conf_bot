import datetime as dt


class DataBase:
    def __init__(self, basefile, scheme):
        import sqlite3
        self.scheme = ''
        try:
            self.conn = sqlite3.connect(basefile, check_same_thread=False)
        except:
            print('Could not connect to DataBase.')
            return None
        with open(scheme, 'r') as scheme_sql:
            sql = scheme_sql.read()
            self.scheme = sql
            if self.conn is not None:
                try:
                    cursor = self.conn.cursor()
                    cursor.executescript(sql)
                except:
                    print('Could not create scheme.')
            else:
                print("Error! cannot create the database connection.")
        print('DB created.')

    def execute(self, sql):
        cursor = self.conn.cursor()
        cursor.execute(sql)
        self.conn.commit()
        return cursor.fetchall()

    def save_word(self, word):
        sql = "INSERT OR IGNORE INTO word('word') VALUES ('%s')" % word
        self.execute(sql)
        sql = "SELECT id FROM word WHERE word = '%s'" % word
        return(self.execute(sql)[0][0])

    def get_alert(self):
        now = dt.datetime.now().strftime("%H%M")
        sql = "SELECT * FROM alert WHERE time = '%s'" % now
        alerts = self.execute(sql)
        sql = "DELETE FROM alert WHERE time = '%s'" % now
        self.execute(sql)
        return alerts

    def add_user(self,
                 username,
                 user_id,
                 first_name,
                 last_name):
        date = int(dt.datetime.now().strftime("%s"))
        try:
            sql = """
            UPDATE user
            SET
                username = '%s',
                first_name = '%s',
                last_name = '%s'
            WHERE
                id = '%s'
            """ % (
                username,
                first_name,
                last_name,
                user_id
            )
            self.execute(sql)
        except:
            pass
        sql = """INSERT OR IGNORE INTO 
        user('id', 'username', 'first_name', 'last_name', 'date') 
        VALUES ('%s','%s','%s','%s','%s')""" % (
            user_id,
            username,
            first_name,
            last_name,
            date
        )
        self.execute(sql)

    def add_conf(self, id, title):
        date = int(dt.datetime.now().strftime("%s"))
        sql = """INSERT OR IGNORE INTO 
        conf('id', 'title', 'date') 
        VALUES ('%s','%s','%s')""" % (
            id,
            title,
            date
        )
        self.execute(sql)

    def add_relation(self, word, user_id, conf_id, text):
        word_id = self.save_word(word)
        date = int(dt.datetime.now().strftime("%s"))
        sql2 = "INSERT OR IGNORE INTO xxx_message('text') VALUES ('%s')" % text
        self.execute(sql2)
        sql3 = "SELECT id FROM `xxx_message` WHERE text = '%s'" % text
        msg_id = self.execute(sql3)[0][0]
        sql = """INSERT OR IGNORE INTO 
        relations('word_id', 'user_id', 'conf_id', 'msg_id', 'date') 
        VALUES ('%s','%s','%s','%s', '%s')""" % (
            word_id,
            user_id,
            conf_id,
            msg_id,
            date
        )
        self.execute(sql)

    def add_alert(self, user_id, conf_id, alert_time, message):
        date = int(dt.datetime.now().strftime("%s"))
        print(alert_time)
        if alert_time[0] == '+':
            alert_time = (dt.datetime.now() + dt.timedelta(minutes=int(alert_time[1:]))).strftime("%H%M")
        sql = """INSERT OR IGNORE INTO 
        alert('conf_id', 'user_id', 'created', 'time', 'message') 
        VALUES ('%s','%s','%s','%s','%s')""" % (
            conf_id,
            user_id,
            date,
            alert_time,
            message
        )
        self.execute(sql)

    def get_top(self, user_id, conf_id, limit=10):
        sql = """
        SELECT w.word, COUNT(*) as count FROM relations r 
        LEFT JOIN word w ON w.id = r.word_id
        LEFT JOIN `user` u ON u.id = r.user_id
        WHERE u.id = '%s' AND
        r.conf_id = '%s' AND
        r.id > (
            SELECT IFNULL(MAX(relation_id), 0) FROM reset WHERE user_id = '%s' AND conf_id = '%s'
        )
        GROUP BY w.word
        ORDER BY count DESC
        LIMIT %s
        """ % (
            user_id,
            conf_id,
            user_id,
            conf_id,
            limit
        )
        result = self.execute(sql)
        return(result)

    def all_conf_users(self, conf_id):
        sql = """
        SELECT DISTINCT(u.username), u.first_name, u.id FROM relations r 
        LEFT JOIN user u 
        ON u.id = r.user_id
        LEFT JOIN conf c 
        ON r.conf_id = c.id
        WHERE c.id = '%s'
        """ % (
            conf_id
        )
        result = self.execute(sql)
        return(result)

    def get_random_word(self, count=1, like="%"):
        sql = "SELECT word FROM word WHERE word LIKE '%s' ORDER BY random() LIMIT %s" % (like, count)
        print(sql)
        result = self.execute(sql)
        return(result)

    def here(self, user_id, conf_id):
        sql = """
        SELECT DISTINCT(u.username), u.id, u.first_name FROM relations r 
        LEFT JOIN user u 
        ON u.id = r.user_id
        LEFT JOIN conf c 
        ON r.conf_id = c.id
        WHERE c.id = '%s' and 
        u.id != '%s'
        """ % (
            conf_id,
            user_id
        )
        result = self.execute(sql)
        return(result)

    def reset(self, user_id, conf_id):
        date = int(dt.datetime.now().strftime("%s"))
        sql = """
        INSERT OR IGNORE INTO reset (user_id, conf_id, date, relation_id) 
        VALUES ('%s', '%s', '%s', (SELECT MAX(rowid) FROM relations));
        """ % (
            user_id,
            conf_id,
            date
        )
        result = self.execute(sql)
        return(result)

    def command(self, sql):
        if 'DELETE' in sql.upper() \
                or 'INSERT' in sql.upper() \
                or 'UPDATE' in sql.upper() \
                or 'DROP' in sql.upper() \
                or 'CREATE' in sql.upper() \
                or 'ALTER' in sql.upper():
            return('gtfo')
        try:
            if 'LIMIT' in sql.upper()[-9:]:
                result = self.execute(sql)
            else:
                result = self.execute(sql + ' limit 20')
        except Exception as err:
            result = err
        return(result)

    def close(self):
        self.conn.close()
