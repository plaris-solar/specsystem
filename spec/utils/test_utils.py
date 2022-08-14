from django.test import TransactionTestCase
import json
import os

AUTH_ERRS = {
                'NO_AUTH': {
                                'msg': 'Authentication credentials were not provided.',
                                'status': 401
                            },
                'BAD_AUTH': {
                                'msg': 'Invalid username/password.',
                                'status': 403
                            },
                'BAD_TOK': {
                                'msg': 'Invalid Token',
                                'status': 401
                            },
                'EXP_TOK': {
                                'msg': 'The Token is expired',
                                'status': 401
                            },
                'PERM_DENIED': {
                                'msg': 'You do not have permission to perform this action.',
                                'status': 403
                            }
             }


class SpecTestCase(TransactionTestCase):

    def setUp(self):
        self.level_tokens = self.get_all_tokens()

    def get_auth_str(self, auth_lvl):
        if auth_lvl:
            return f'token {self.level_tokens[auth_lvl]}'
        return ''

    def post_request(self, url, body=None, file=None, auth_lvl=''):
        if file:
            fp = open(file, 'rb')
            body['FILE'] = fp
            return self.client.post(url, body, HTTP_AUTHORIZATION=self.get_auth_str(auth_lvl))
        return self.client.post(url, body, 'application/json', HTTP_AUTHORIZATION=self.get_auth_str(auth_lvl))

    def put_request(self, url, body, auth_lvl='ADMIN'):
        return self.client.put(url, body, 'application/json', HTTP_AUTHORIZATION=self.get_auth_str(auth_lvl))

    def get_request(self, url, auth_lvl=''):
        return self.client.get(url, HTTP_AUTHORIZATION=self.get_auth_str(auth_lvl))

    def delete_request(self, url, body=None, auth_lvl=''):
        return self.client.delete(url, body, content_type='application/json',
                                  HTTP_AUTHORIZATION=self.get_auth_str(auth_lvl))

    def delete_list_attribs(self, item_list, attrib_list, meta_key=True):
        for i, item in enumerate(item_list):
            if meta_key:
                item_list[i]['data'] = self.delete_attribs(item['data'], attrib_list)
            item_list[i] = self.delete_attribs(item, attrib_list)
        return item_list

    def delete_attribs(self, item, attrib_list):
        if item:
            for attrib in attrib_list:
                if attrib in item.keys():
                    item.pop(attrib)
        return item

    def data_to_list(self, data, id_col='lot_id', add_row_num=False):
        doc_type = data['doc_type']

        ret_list = []
        for d in data['data']:
            ret_list.append({'doc_type': doc_type, '_id': d[id_col], 'data': d})
        if add_row_num:
            ret_list = self.add_row_num(ret_list)
        return ret_list

    def assert_schema_err(self, response, err_field):
        resp = json.loads(response)
        self.assertIn("schemaErrors", resp)
        self.assertIn(err_field, resp['schemaErrors'])
        self.assertGreaterEqual(len(resp['schemaErrors'][err_field]), 1)

    def add_row_num(self, data):
        for idx, d in enumerate(data):
            d['row_num'] = idx + 2
        return data

    def load_page(self, data):
        data = json.loads(data)
        return data['results']

    def get_all_tokens(self):
        # get csrf token
        resp = self.client.get('/accounts/login/')
        tok = resp.cookies['csrftoken'].value

        # Login via csrf token + djagno LDAP
        auth_body = {'username': os.getenv('USER_USER'), 'password': os.getenv('USER_PASSWD')}
        response = self.client.post('/accounts/login/', auth_body)
        self.assertEqual(response.status_code, 302)

        # Login via csrf token + djagno LDAP
        auth_body = {'username': os.getenv('ADMIN_USER'), 'password': os.getenv('ADMIN_PASSWD')}
        response = self.client.post('/accounts/login/', auth_body)
        self.assertEqual(response.status_code, 302)

        # Set token
        headers = {
                    'Content-Type': 'application/json',
                }

        response = self.client.post(f'/auth/token/{os.getenv(f"ADMIN_USER")}', **headers)
        self.assertEqual(response.status_code, 200)
        resp = json.loads(response.content)
        admin_tok = resp['Authorization']

        response = self.client.post(f'/auth/token/{os.getenv(f"USER_USER")}', **headers)
        self.assertEqual(response.status_code, 200)
        resp = json.loads(response.content)
        user_tok = resp['Authorization']

        response = self.client.post('/accounts/logout/', auth_body)
        self.assertEqual(response.status_code, 200)

        return {'USER': user_tok, 'ADMIN': admin_tok}

    def assert_auth_error(self, response, err_type):
        exp_response = AUTH_ERRS[err_type]
        self.assertEqual(response.status_code, exp_response['status'])
        resp = json.loads(response.content)
        self.assertEqual(resp['detail'], exp_response['msg'])

