import json
import datetime
import cx_Oracle as oracle
from .my_logger import logger

class DB_Connection(object):
    def __init__(self):
        self.log = logger()
        with open('./configuration.json') as f:
            data = json.load(f)
            db_connection = data['db_connection']

        self.ip = db_connection['ip']
        self.username = db_connection['username']
        self.password = db_connection['password']
        self.oracle_port = db_connection['oracle_port']
        self.oracle_service = db_connection['oracle_service']
        self.database = None
        self.cursor = None

    def open_connection(self):
        self.database = oracle.connect(self.username + "/" + self.password + "@" + self.ip + ":" + self.oracle_port + "/" + self.oracle_service)
        self.cursor = self.database.cursor()

    def close_connection(self):
        self.cursor.close()  # 关闭cursor
        self.database.close()

    def get_unfinish_page(self):
        select_sql = "select CASE_TYPE, PAGE_NUM from CHN_COURT_SUPPORT where status = 0"
        self.cursor.execute(select_sql)
        results = self.cursor.fetchall()
        return results

    def get_unfinish_detail(self):
        select_sql = "select DOC_ID, DOCUMENT_ID, FILE_SITE from CHN_COURT_SENTENCE where status = 0"
        self.cursor.execute(select_sql)
        results = self.cursor.fetchall()
        return results

    def save_list_info(self, item):
        try:
            insert_sql = "insert into SCOTT.CHN_COURT_SENTENCE(DOC_ID, DOCUMENT_ID, DOCUMENT_DATE, PUNISH_ORG, " \
                         "DOCUMENT_TYPE1, DOCUMENT_TYPE2, PUNISH_TITLE, FILE_SITE, status, creator) " \
                         "values (:1, :2, :3, :4, :5, :6, :7, :8, 0, 'gc')"
            self.cursor.execute(insert_sql, [item.id, item.doc_id, item.doc_date, item.pun_org, item.case_type,
                                             item.doc_type, item.pun_title, item.file_path])
            self.cursor.connection.commit()
        except Exception as e:
            self.log.error(e)
            return False
        return True

    def save_details(self, item):
        try:
            update_sql = "update SCOTT.CHN_COURT_SENTENCE set PUB_DATE = to_date(:1, 'YYYY-MM-DD'), " \
                         "PUNISH_FACTS = :2, DOCUMENT_ID = :3, status = 1, UPDATETIME = :4" \
                         "where DOC_ID = :5"
            clob_data = self.cursor.var(oracle.CLOB)
            clob_data.setvalue(0, item.pun_fact)

            # 插入
            # self.cursor.prepare(update_sql)

            # self.cursor.setinputsizes(PUNISH_FACTS=oracle.CLOB)
            self.cursor.execute(update_sql, [item.pub_date, clob_data.values[0], item.doc_id, datetime.datetime.now(), item.id])
            # self.cursor.execute(update_sql, [item.pub_date, item.pun_fact, item.doc_id, datetime.datetime.now(), item.id])
            self.cursor.connection.commit()
        except Exception as e:
            self.log.error(e)
            # self.log.error(update_sql)

    def update_finished(self, case_type, page):
        update_sql = "update CHN_COURT_SUPPORT set " \
                     "STATUS = 1, EDIT_TIME = :1 " \
                     "where CASE_TYPE = :2 and PAGE_NUM = :3"
        self.cursor.execute(update_sql, [datetime.datetime.now(), case_type, page])
        self.cursor.connection.commit()

    def clear_finished(self):
        update_sql = "update CHN_COURT_SUPPORT set STATUS = 0, EDIT_TIME = :1"
        self.cursor.execute(update_sql, [datetime.datetime.now()])
        self.cursor.connection.commit()

    def identify_unfinished(self):
        update_sql = "update CHN_COURT_SENTENCE set STATUS = 0 where PUB_DATE is NULL"
        self.cursor.execute(update_sql)
        self.cursor.connection.commit()
