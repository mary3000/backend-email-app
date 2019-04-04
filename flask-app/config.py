import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = 'foobarbaz'

    DBUSER = 'marco'
    DBPASS = 'foobarbaz'
    DBHOST = 'db'
    DBPORT = '5432'
    DBNAME = 'testdb'

    SQLALCHEMY_DATABASE_URI = \
        'postgresql+psycopg2://{user}:{passwd}@{host}:{port}/{db}'.format(
            user=DBUSER,
            passwd=DBPASS,
            host=DBHOST,
            port=DBPORT,
            db=DBNAME)

    SQLALCHEMY_TRACK_MODIFICATIONS = False