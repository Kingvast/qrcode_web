from cloudant.client import CouchDB


def test_connect_db():
    user = 'develop'
    password = 'devpwd'
    client = CouchDB(user, password, url='http://couchdb:5984')
