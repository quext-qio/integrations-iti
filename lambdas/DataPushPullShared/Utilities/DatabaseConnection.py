import datetime
from datetime import date
from decimal import Decimal

import mysql.connector
import pymysql
from sshtunnel import SSHTunnelForwarder

from DataPushPullShared.Utilities.DataController import Datasource
from DataPushPullShared.Config.DatabaseConfig import configDevNewCo
from DataPushPullShared.Config.DatabaseConfig import configProdNewCo
from DataPushPullShared.Config.DatabaseConfig import ssh_configDevNewCo
from DataPushPullShared.Utilities.DatabaseQueries import getQuery


def executeQuery(query_string: str, _config: dict, _ssh_config: dict, params: list = None):
    _query, _fields = getQuery(query_string)
    _query = _query.replace('DATABASE_NAME', _config['database'])

    if not bool(_ssh_config):
        conn = mysql.connector.connect(host=_config['host'],
                                       port=_config['port'],
                                       user=_config['user'],
                                       password=_config['password'],
                                       db=_config['database'])
        cursor = conn.cursor()

        if params is not None:

            recordset = []
            for item in params:
                cursor.execute(_query, item)
                for line in cursor:
                    record = {}
                    for label, value in zip(_fields, line):
                        if isinstance(value, date):
                            record[label] = value.strftime("%d-%b-%Y")
                        elif isinstance(value, Decimal):
                            record[label] = str(value)
                        else:
                            record[label] = value
                    recordset.append(record)
        else:
            cursor.execute(_query)
            recordset = []
            for line in cursor:
                record = {}
                for label, value in zip(_fields, line):
                    if isinstance(value, date):
                        record[label] = value.strftime("%d-%b-%Y")
                    else:
                        record[label] = value
                recordset.append(record)
        cursor.close()
        conn.close()
        return recordset
    else:
        with SSHTunnelForwarder(
                (_ssh_config['host'], 22),
                ssh_username=_ssh_config['user'],
                ssh_private_key=_ssh_config['key'],
                remote_bind_address=(_config['host'], _config['port'])
        ) as server:
            conn = pymysql.connect(host=_config['host'],
                                   port=server.local_bind_port,
                                   user=_config['user'],
                                   passwd=_config['password'],
                                   db=_config['database'])
            cursor = conn.cursor()

            if params is not None:
                recordset = []
                for item in params:
                    cursor.execute(_query, item)
                    for line in cursor:
                        record = {}
                        for label, value in zip(_fields, line):
                            if isinstance(value, date):
                                record[label] = value.strftime("%d-%b-%Y")
                            elif isinstance(value, Decimal):
                                record[label] = str(value)
                            else:
                                record[label] = value
                        recordset.append(record)
            else:
                cursor.execute(_query)
                recordset = []
                for line in cursor:
                    record = {}
                    for label, value in zip(_fields, line):
                        if isinstance(value, date):
                            record[label] = value.strftime("%d-%b-%Y")
                        else:
                            record[label] = value
                    recordset.append(record)
            cursor.close()
            conn.close()
            return recordset


def getConfigData(_type: Datasource):
    switcher = {
        Datasource.NEWCO_PROD: configProdNewCo,
        Datasource.NEWCO_DEV: configDevNewCo,
        Datasource.NONE: {}
    }
    return switcher.get(_type, {})


def getSSHConfigData(_type: Datasource):
    switcher = {
        Datasource.NEWCO_DEV: ssh_configDevNewCo,
        Datasource.NONE: {}
    }
    return switcher.get(_type, {})
