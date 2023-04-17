import os

configProdNewCo = {
    'user': 'zato',
    'password': f'{os.environ["NEWCO_DB_PASSWORD"]}',
    'host': 'newco-prod-readonly2.czlebpbzjy34.us-east-2.rds.amazonaws.com',
    'port': 3306,
    'database': 'forge',
    'raise_on_warnings': False
}
configDevNewCo = {
    'user': 'quext-ie',
    'password': f'{os.environ["NEWCO_DB_DEV_PASSWORD"]}',
    'host': '127.0.0.1',
    'port': 3306,
    'database': 'envTest',
    'raise_on_warnings': False
}
ssh_configDevNewCo = {
    'user': "forge",
    "host": "18.218.52.238",
    "key": "/opt/zato/3.1.0/code/zato_extra_paths/DataPushPullShared/ie2newcoDev-private-key"
}

database_key = {
    "newco_key": "GpCj0YdRNBe7a+18523WF6yE1zFy+6Bo3fQyaPdFjHs="
}
