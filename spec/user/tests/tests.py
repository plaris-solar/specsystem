import json, os
from django.conf import settings
from rest_framework.exceptions import ValidationError
from utils.test_utils import SpecTestCase
from django.contrib.auth.models import User as DjangoUser
from user.models import User
from . import test_resources as tr

TEST_FILE_DIR = 'data/tests/test_files/'


class UserTest(SpecTestCase):

    def test_token(self):

        # Post token for dummy user
        response = self.post_request('/auth/token/dummy', auth_lvl='USER')
        self.assert_auth_error(response, 'PERM_DENIED')

        # Post token for dummy user
        response = self.post_request('/auth/token/dummy', auth_lvl='ADMIN')
        self.assertEqual(response.status_code, 400)
        resp = json.loads(response.content)
        self.assertIn('error', resp)
        self.assertEqual('Specified user: dummy does not exist.', resp['error'])

        # Post admin token
        response = self.post_request(f'/auth/token/{os.getenv("ADMIN_USER")}', auth_lvl='ADMIN')
        self.assertEqual(response.status_code, 200)
        resp = json.loads(response.content)
        self.assertIn('Authorization', resp)
        admin_tok = resp['Authorization']

        # Get admin token
        response = self.get_request('/auth/token')
        self.assert_auth_error(response, 'NO_AUTH')

        # Get admin token
        response = self.get_request('/auth/token', auth_lvl='ADMIN')
        self.assertEqual(response.status_code, 200)
        resp = json.loads(response.content)
        self.assertEqual(resp[0]['user'], os.environ['ADMIN_USER'])
        self.assertEqual(resp[0]['expired'], False)

        # Verify token auth
        response = self.client.get('/auth/token', HTTP_AUTHORIZATION=f'token {admin_tok}')
        self.assertEqual(response.status_code, 200)

        # Delete operator token
        response = self.delete_request(f'/auth/token/{os.environ["ADMIN_USER"]}', auth_lvl='USER')
        self.assert_auth_error(response, 'PERM_DENIED')

        # Delete dummy token
        response = self.client.delete(f'/auth/token/dummy',
                                      HTTP_AUTHORIZATION=f'token {admin_tok}')
        self.assertEqual(response.status_code, 400)
        resp = json.loads(response.content)
        self.assertIn('error', resp)
        self.assertEqual('Specified user: dummy does not exist.', resp['error'])

        # Delete operator token
        response = self.client.delete(f'/auth/token/{os.environ["ADMIN_USER"]}', HTTP_AUTHORIZATION=f'token {admin_tok}')
        self.assertEqual(response.status_code, 204)

        # Verify token deletion
        response = self.client.get('/auth/token', HTTP_AUTHORIZATION=f'token {admin_tok}')
        self.assert_auth_error(response, 'BAD_TOK')

    def test_permissions(self):
        response = self.get_request('/auth/info')
        self.assert_auth_error(response, 'NO_AUTH')

        response = self.get_request('/auth/info', auth_lvl='ADMIN')
        self.assertEqual(response.status_code, 200)
        resp = json.loads(response.content)
        self.assertEqual(resp['is_admin'], True)

    def test_token_expiration(self):
        # Set the token expiration time to 0 so tokens expire instantly
        exp_time = settings.TOKEN_EXPIRED_AFTER_SECONDS
        settings.TOKEN_EXPIRED_AFTER_SECONDS = 0

        # Get operator token via token auth
        # Error- token is expired
        response = self.get_request('/auth/token', auth_lvl='ADMIN')
        self.assert_auth_error(response, 'EXP_TOK')

        # Login via djagno LDAP because admin tokens are expired
        auth_body = {'username': os.getenv('ADMIN_USER'), 'password': os.getenv('ADMIN_PASSWD')}
        response = self.client.post('/accounts/login/', auth_body)
        self.assertEqual(response.status_code, 302)

        # verify token is expired through token info interface
        response = self.client.get('/auth/token')
        self.assertEqual(response.status_code, 200)
        resp = json.loads(response.content)
        self.assertEqual(resp[0]['user'], os.environ['ADMIN_USER'])
        self.assertEqual(resp[0]['expired'], True)

        # Reset token expiration time
        settings.TOKEN_EXPIRED_AFTER_SECONDS = exp_time

        # Post new admin token using session auth
        response = self.post_request(f'/auth/token/{os.getenv("ADMIN_USER")}')
        self.assertEqual(response.status_code, 200)
        resp = json.loads(response.content)
        self.assertIn('Authorization', resp)
        admin_tok = resp['Authorization']

        response = self.client.post('/accounts/logout/', auth_body)
        self.assertEqual(response.status_code, 200)

        # Verify new token auth and that the old expired token has been deleted
        response = self.client.get('/auth/token', HTTP_AUTHORIZATION=f'token {admin_tok}')
        self.assertEqual(response.status_code, 200)
        resp = json.loads(response.content)
        self.assertEqual(len(resp), 2)
        self.assertEqual(resp[0]['user'], os.environ['ADMIN_USER'])
        self.assertEqual(resp[0]['expired'], False)

    def test_user_lookup(self):
        """Unit test for user.models.User.lookup()"""
        user = User.lookup(os.environ['USER_USER'])
        self.assertIsNotNone(user)

        user = DjangoUser.objects.filter(username=os.environ['USER_USER']).first()
        user.is_active = False
        user.save()

        with self.assertRaises(ValidationError) as ve:
            user = User.lookup(os.environ['USER_USER'])
        self.assertEqual(ve.exception.detail['error'], f"User: {os.environ['USER_USER']} is not an active account.")

        user.delete()
        with self.assertRaises(ValidationError) as ve:
            user = User.lookup('BAD_USER_NAME')
        self.assertEqual(ve.exception.detail['error'], "User: BAD_USER_NAME does not exist.")
