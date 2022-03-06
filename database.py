import sqlite3
import os


class Database:
    def __init__(self, database_path: str):
        """

        :param database_path: path to your database
        """
        self.database = database_path

        con = sqlite3.connect(f"{self.database}")
        con.commit()
        con.close()

    def make_dir(self, path):
        """

        :param path:
        :return:
        """

        if not os.path.exists(path):
            return os.mkdir(path)
        else:
            return False

    def create_table(self, table_name: str, columns: list):
        """

        :param table_name: the name of the table to be crated in database
        :param columns: columns of the table
        :return:
        """
        con = sqlite3.connect(f"{self.database}")
        cur = con.cursor()
        # check if table already exist
        res = [i[0] for i in cur.execute(f"""SELECT name FROM sqlite_master WHERE type='table'""").fetchall()]
        if table_name in res:
            # table already exist
            return False
        else:
            cur.execute(f"""CREATE TABLE {table_name} ({', '.join([str(i) for i in columns])})""")
            return True

    def inset_into(self, table_name: str, insert_info: list) -> list:
        """

        :param table_name: name table in database
        :param insert_info: list of information that will be inserted into your database
        :return:
        """
        insert_info = [str(i) for i in insert_info]

        con = sqlite3.connect(f"{self.database}")
        cur = con.cursor()
        cur.execute(f"""INSERT INTO {table_name} VALUES ({('?, ' * len(insert_info))[:-2]})""", insert_info)
        result = [i for i in cur.execute(f"""SELECT * FROM {table_name}""")]
        con.commit()
        con.close()
        return result

    def select(self, table_name, columns="*"):
        """

        :param table_name:
        :param columns:
        :return:
        """
        con = sqlite3.connect(f"{self.database}")
        cur = con.cursor()
        res = [i[0] for i in cur.execute(f"""SELECT name FROM sqlite_master WHERE type='table'""").fetchall()]
        if table_name in res:
            if columns == '*':
                result = [i for i in cur.execute(f"""SELECT {columns} FROM {table_name}""").fetchall()]
                return result
            result = [i for i in cur.execute(
                f"""SELECT {", ".join([str(i) for i in columns])} FROM {table_name}""").fetchall()]
            return result
        else:
            return False

    def select_by_user_id(self, table_name, user_id):
        """

        :param table_name:
        :param user_id:
        :return:
        """
        con = sqlite3.connect(f"{self.database}")
        cur = con.cursor()

        res = cur.execute(f"""SELECT * FROM {table_name} WHERE user_id='{user_id}'""")
        res = [i for i in res]

        con.commit()
        con.close()

        return res


if __name__ == '__main__':
    database = Database('db.db')
    # database.create_table("admin", ["user_id", "name", "date", "is_admin"])
    # database.create_table("stop", ["user_id", "stopped", "date"])
    # database.create_table("users", ["user_id", "name", "date"])
    # database.create_table("other", ["user_id", "json"])

    post_database = Database('posts/post_db.db')
    # post_database.create_table('post', ['post_id', 'user_id', 'username', 'data', 'text', 'images'])

    statics = Database('stats.db')
    statics.create_table('new_message', ['user_id', 'event', 'json'])

    log = Database('log.db')
    log.create_table('logs', ['user_id', 'event', 'what_happening', 'date'])

    # import datetime
    # database.inset_into('admin', ['1587872539', 'wawilow', f"{datetime.datetime.now()}", '1'])