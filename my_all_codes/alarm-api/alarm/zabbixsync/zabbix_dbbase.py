# -*- encoding:gb2312 -*-_
__author__ = 'root'
'''
Created on 2016-1-21
@author: gaga.Yan
'''
from oslo_config import cfg
import MySQLdb
import MySQLdb.cursors


STORE_RESULT_MODE = 0
USE_RESULT_MODE = 1

CURSOR_MODE = 0
DICTCURSOR_MODE = 1
SSCURSOR_MODE = 2
SSDICTCURSOR_MODE = 3

FETCH_ONE = 0
FETCH_MANY = 1
FETCH_ALL = 2

CONF = cfg.CONF
auth = [
    cfg.StrOpt('zabbix_db_host',
               default='127.0.0.1', help=''),
    cfg.StrOpt('zabbix_db_user', default='admin', help=''),
    cfg.StrOpt('zabbix_db_password', default='123456', help=''),
    cfg.StrOpt('zabbix_db_name', default='zabbix', help=''),
    cfg.IntOpt('zabbix_db_port', default=3306, help=''),
]
CONF.register_opts(auth)


class PyMysql(object):
    # singleton
    _instance = None

    def __init__(self):
        self.conn = None

    @staticmethod
    def get_instance():
        if not PyMysql._instance:
            PyMysql._instance = PyMysql()
        return PyMysql._instance

    def newConnection(self, host=CONF.zabbix_db_host, user=CONF.zabbix_db_user, passwd=CONF.zabbix_db_password,
                      defaultdb=CONF.zabbix_db_name, port=CONF.zabbix_db_port):
        """
        ����һ�������ӣ�ָ��host���û��������롢Ĭ�����ݿ⡢�˿�
        """
        self.conn = MySQLdb.Connect(host, user, passwd, defaultdb, port, charset="utf8")
        if not self.conn.open:
            raise None

    def closeConnnection(self):
        """
        �رյ�ǰ����
        """
        self.conn.close()

    def commit(self):
        """
        �ύ
        """
        self.conn.commit()

    def query(self, sqltext, mode=STORE_RESULT_MODE):
        """
        ���ã�ʹ��connection�����query������������һ��Ԫ��(Ӱ������(int),�����(result))
        ������sqltext��sql���
             mode=STORE_RESULT_MODE��0�� ��ʾ����store_result��mode=USESTORE_RESULT_MODE��1�� ��ʾ����use_result
        ���أ�Ԫ��(Ӱ������(int),�����(result)
        """
        if self.conn == None or self.conn.open == False:
            return -1
        self.conn.query(sqltext)
        if mode == 0:
            result = self.conn.store_result()
        elif mode == 1:
            result = self.conn.use_result()
        else:
            raise Exception("mode value is wrong.")
        return result

    def fetch_queryresult(self, result, how=0, moreinfo=False):
        """
        ����:result�� query��Ľ������
            maxrows�� ���ص��������
            how�� �Ժ��ַ�ʽ�洢���
             (0��tuple,1��dictionaries with columnname,2��dictionaries with table.columnname)
            moreinfo ��ʾ�Ƿ��ȡ���������Ϣ��num_fields��num_rows,num_fields��
        ���أ�Ԫ�飨���ݼ���������Ϣ����moreinfo=False����һ���ݼ�����moreinfo=True��
        """
        if result == None:
            return None
        dataset = result.fetch_row(how)
        if moreinfo is False:
            return dataset
        else:
            num_fields = result.num_fields()
            num_rows = result.num_rows()
            field_flags = result.field_flags()
            info = (num_fields, num_rows, field_flags)
            return (dataset, info)

    def execute(self, sqltext, args=None, mode=CURSOR_MODE, many=False):
        """
        ���ã�ʹ���α꣨cursor����execute ִ��query
        ������sqltext�� ��ʾsql���
             args�� sqltext�Ĳ���
             mode���Ժ��ַ�ʽ�������ݼ�
                CURSOR_MODE = 0 ��store_result , tuple
                DICTCURSOR_MODE = 1 �� store_result , dict
                SSCURSOR_MODE = 2 : use_result , tuple
                SSDICTCURSOR_MODE = 3 : use_result , dict
             many���Ƿ�ִ�ж��в�����executemany��
        ���أ�Ԫ�飨Ӱ��������int�����α꣨Cursor����
        """
        if mode == CURSOR_MODE:
            curclass = MySQLdb.cursors.Cursor
        elif mode == DICTCURSOR_MODE:
            curclass = MySQLdb.cursors.DictCursor
        elif mode == SSCURSOR_MODE:
            curclass = MySQLdb.cursors.SSCursor
        elif mode == SSDICTCURSOR_MODE:
            curclass = MySQLdb.cursors.SSDictCursor
        else:
            raise Exception("mode value is wrong")

        cur = self.conn.cursor(cursorclass=curclass)
        line = 0
        if many == False:
            if args == None:
                line = cur.execute(sqltext)
            else:
                line = cur.execute(sqltext, args)
        else:
            if args == None:
                line = cur.executemany(sqltext)
            else:
                line = cur.executemany(sqltext, args)
        return line

    def fetch_executeresult(self, cursor, mode=FETCH_ONE, rows=1):
        """
        ���ã���ȡcursor��ȡ�����ݼ�
        ������cursor���α�
             mode��ִ����ȡģʽ
              FETCH_ONE: ��ȡһ���� FETCH_MANY :��ȡrows�� ��FETCH_ALL : ��ȡ����
             rows����ȡ����
        ���أ�fetch���ݼ�
        """
        if cursor == None:
            return
        if mode == FETCH_ONE:
            return cursor.fetchone()
        elif mode == FETCH_MANY:
            return cursor.fetchmany(rows)
        elif mode == FETCH_ALL:
            return cursor.fetchall()


if __name__ == "__main__":
    print help(PyMysql)