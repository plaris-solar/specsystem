import copy
import json
from django.conf import settings
from utils.test_utils import SpecTestCase
from utils import test_utils
from . import test_resources as tr

class SpecTest(SpecTestCase):

    def test_role(self):
        response = self.post_request('/role/', tr.role_post_1, auth_lvl='USER')
        self.assert_auth_error(response, 'PERM_DENIED')

        response = self.post_request('/role/', tr.role_post_1, auth_lvl='ADMIN')
        self.assertEqual(response.status_code, 201)
        
        response = self.post_request('/role/', tr.role_post_2, auth_lvl='ADMIN')
        self.assertEqual(response.status_code, 201)
        
        response = self.post_request('/role/', tr.role_post_3, auth_lvl='ADMIN')
        self.assertEqual(response.status_code, 201)

        # Duplicate
        response = self.post_request('/role/', tr.role_post_1, auth_lvl='ADMIN')
        self.assertEqual(response.status_code, 400)
        resp = json.loads(response.content)
        self.assertIn('already exists', str(response.content))

        # Error - invalid character in role name
        err_body = copy.deepcopy(tr.role_post_1)
        err_body['role'] = 'Name with Space'
        response = self.post_request('/role/', err_body, auth_lvl='ADMIN')
        self.assertEqual(response.status_code, 400)
        resp = json.loads(response.content)
        self.assertIn('Role names cannot contain special characters', resp['error'])

        # Error - role name missing
        err_body['role'] = None
        response = self.post_request('/role/', err_body, auth_lvl='ADMIN')
        self.assertEqual(response.status_code, 400)
        self.assert_schema_err(response.content, 'role')

        # List all roles with 'Op' in name
        response = self.get_request('/role/?search=Op')
        self.assertEqual(response.status_code, 200)
        resp = json.loads(response.content)
        self.assertEqual(resp, self.paginate_results([tr.role_post_2, tr.role_post_3]))

        # Error: Update role with spec_one a number (not a boolean)
        response = self.put_request(f'/role/{tr.role_put_1["role"]}', tr.role_put_err_1, auth_lvl='ADMIN')
        self.assertEqual(response.status_code, 400)
        self.assert_schema_err(response.content, 'spec_one')

        # Update role
        response = self.put_request(f'/role/{tr.role_put_1["role"]}', tr.role_put_1, auth_lvl='ADMIN')
        self.assertEqual(response.status_code, 200)

        # Get updated role
        response = self.get_request(f'/role/{tr.role_put_1["role"]}')
        self.assertEqual(response.status_code, 200)
        resp = json.loads(response.content)
        self.assertEqual(resp, tr.role_put_1)

        # Error: permissions
        response = self.delete_request(f'/role/{tr.role_put_1["role"]}')
        self.assert_auth_error(response, 'NO_AUTH')
        response = self.delete_request(f'/role/{tr.role_put_1["role"]}', auth_lvl='USER')
        self.assert_auth_error(response, 'PERM_DENIED')

        # Delete updated role
        response = self.delete_request(f'/role/{tr.role_put_1["role"]}', auth_lvl='ADMIN')
        self.assertEqual(response.status_code, 204)

        # Get deleted role
        response = self.get_request(f'/role/{tr.role_put_1["role"]}')
        self.assertEqual(response.status_code, 400)
        resp = json.loads(response.content)
        self.assertEqual(resp['error'], f"Role ({tr.role_put_1['role']}) does not exist.")


    def test_dept(self):
        # Load needed roles
        response = self.post_request('/role/', tr.role_post_1, auth_lvl='ADMIN')
        self.assertEqual(response.status_code, 201)        
        response = self.post_request('/role/', tr.role_post_2, auth_lvl='ADMIN')
        self.assertEqual(response.status_code, 201)        
        response = self.post_request('/role/', tr.role_post_3, auth_lvl='ADMIN')
        self.assertEqual(response.status_code, 201)

        response = self.post_request('/dept/', tr.dept_post_1, auth_lvl='USER')
        self.assert_auth_error(response, 'PERM_DENIED')

        response = self.post_request('/dept/', tr.dept_post_1, auth_lvl='ADMIN')
        self.assertEqual(response.status_code, 201)
        
        response = self.post_request('/dept/', tr.dept_post_2, auth_lvl='ADMIN')
        self.assertEqual(response.status_code, 201)
        
        response = self.post_request('/dept/', tr.dept_post_3, auth_lvl='ADMIN')
        self.assertEqual(response.status_code, 201)

        # Duplicate
        response = self.post_request('/dept/', tr.dept_post_1, auth_lvl='ADMIN')
        self.assertEqual(response.status_code, 400)
        resp = json.loads(response.content)
        self.assertIn('already exists', str(response.content))

        # Error - invalid character in dept name
        err_body = copy.deepcopy(tr.dept_post_1)
        err_body['name'] = 'Name with Space'
        response = self.post_request('/dept/', err_body, auth_lvl='ADMIN')
        self.assertEqual(response.status_code, 400)
        resp = json.loads(response.content)
        self.assertIn('Department names cannot contain special characters', resp['error'])

        # Error - dept name missing
        err_body['name'] = None
        response = self.post_request('/dept/', err_body, auth_lvl='ADMIN')
        self.assertEqual(response.status_code, 400)
        self.assert_schema_err(response.content, 'name')

        # List all depts with 'Op' in name
        response = self.get_request('/dept/?search=Op')
        self.assertEqual(response.status_code, 200)
        resp = json.loads(response.content)
        self.assertEqual(resp, self.paginate_results([tr.dept_post_2, tr.dept_post_3]))

        # Error: Update dept with readRoles as number (not a str)
        response = self.put_request(f'/dept/{tr.dept_put_1["name"]}', tr.dept_put_err_1, auth_lvl='ADMIN')
        self.assertEqual(response.status_code, 400)
        self.assert_schema_err(response.content, 'readRoles')

        # Error: Update dept with readRoles incl BadRole
        response = self.put_request(f'/dept/{tr.dept_put_1["name"]}', tr.dept_put_err_2, auth_lvl='ADMIN')
        self.assertEqual(response.status_code, 400)
        resp = json.loads(response.content)
        self.assertIn('Role: BadRole does not exist.', resp['error'])

        # Update dept
        response = self.put_request(f'/dept/{tr.dept_put_1["name"]}', tr.dept_put_1, auth_lvl='ADMIN')
        self.assertEqual(response.status_code, 200)

        # Get updated dept
        response = self.get_request(f'/dept/{tr.dept_put_1["name"]}')
        self.assertEqual(response.status_code, 200)
        resp = json.loads(response.content)
        self.assertEqual(resp, tr.dept_put_1)

        # Error: permissions
        response = self.delete_request(f'/dept/{tr.dept_put_1["name"]}')
        self.assert_auth_error(response, 'NO_AUTH')
        response = self.delete_request(f'/dept/{tr.dept_put_1["name"]}', auth_lvl='USER')
        self.assert_auth_error(response, 'PERM_DENIED')

        # Delete updated dept
        response = self.delete_request(f'/dept/{tr.dept_put_1["name"]}', auth_lvl='ADMIN')
        self.assertEqual(response.status_code, 204)

        # Get deleted dept
        response = self.get_request(f'/dept/{tr.dept_put_1["name"]}')
        self.assertEqual(response.status_code, 400)
        resp = json.loads(response.content)
        self.assertEqual(resp['error'], f"Department ({tr.dept_put_1['name']}) does not exist.")


    def test_doctype(self):
        response = self.post_request('/doctype/', tr.doctype_post_1, auth_lvl='USER')
        self.assert_auth_error(response, 'PERM_DENIED')

        response = self.post_request('/doctype/', tr.doctype_post_1, auth_lvl='ADMIN')
        self.assertEqual(response.status_code, 201)
        
        response = self.post_request('/doctype/', tr.doctype_post_2, auth_lvl='ADMIN')
        self.assertEqual(response.status_code, 201)
        
        response = self.post_request('/doctype/', tr.doctype_post_3, auth_lvl='ADMIN')
        self.assertEqual(response.status_code, 201)

        # Duplicate
        response = self.post_request('/doctype/', tr.doctype_post_1, auth_lvl='ADMIN')
        self.assertEqual(response.status_code, 400)
        resp = json.loads(response.content)
        self.assertIn('already exists', str(response.content))

        # Error - invalid character in doctype name
        err_body = copy.deepcopy(tr.doctype_post_1)
        err_body['name'] = 'Name with Space'
        response = self.post_request('/doctype/', err_body, auth_lvl='ADMIN')
        self.assertEqual(response.status_code, 400)
        resp = json.loads(response.content)
        self.assertIn('Document Type names cannot contain special characters', resp['error'])

        # Error - doctype name missing
        err_body['name'] = None
        response = self.post_request('/doctype/', err_body, auth_lvl='ADMIN')
        self.assertEqual(response.status_code, 400)
        self.assert_schema_err(response.content, 'name')

        # List all doctypes with 'Op' in descr
        response = self.get_request('/doctype/?search=Op')
        self.assertEqual(response.status_code, 200)
        resp = json.loads(response.content)
        expected = self.paginate_results([tr.doctype_post_1, tr.doctype_post_2])
        for e in expected['results']:            
            if e['jira_temp'] is not None and len(e['jira_temp']) > 0 \
                and settings.JIRA_URI is not None and len(settings.JIRA_URI) > 0:
                e['jira_temp_url'] = f'{settings.JIRA_URI}/browse/{e["jira_temp"]}'
            if settings.JIRA_URI is not None or len(settings.JIRA_URI) > 0:
                e['jira_temp_url_base'] = f'{settings.JIRA_URI}/browse/'
        self.assertEqual(resp, expected)

        # Error: Update doctype with readRoles as number (not a str)
        response = self.put_request(f'/doctype/{tr.doctype_put_1["name"]}', tr.doctype_put_err_1, auth_lvl='ADMIN')
        self.assertEqual(response.status_code, 400)
        self.assert_schema_err(response.content, 'confidential')

        # Update doctype
        response = self.put_request(f'/doctype/{tr.doctype_put_1["name"]}', tr.doctype_put_1, auth_lvl='ADMIN')
        self.assertEqual(response.status_code, 200)

        # Get updated doctype
        response = self.get_request(f'/doctype/{tr.doctype_put_1["name"]}')
        self.assertEqual(response.status_code, 200)
        resp = json.loads(response.content)
        expected = copy.deepcopy(tr.doctype_put_1)
        if expected['jira_temp'] is not None and len(expected['jira_temp']) > 0 \
            and settings.JIRA_URI is not None and len(settings.JIRA_URI) > 0:
            expected['jira_temp_url'] = f'{settings.JIRA_URI}/browse/{expected["jira_temp"]}'
        if settings.JIRA_URI is not None or len(settings.JIRA_URI) > 0:
            expected['jira_temp_url_base'] = f'{settings.JIRA_URI}/browse/'
        self.assertEqual(resp, expected)

        # Error: permissions
        response = self.delete_request(f'/doctype/{tr.doctype_put_1["name"]}')
        self.assert_auth_error(response, 'NO_AUTH')
        response = self.delete_request(f'/doctype/{tr.doctype_put_1["name"]}', auth_lvl='USER')
        self.assert_auth_error(response, 'PERM_DENIED')

        # Delete updated doctype
        response = self.delete_request(f'/doctype/{tr.doctype_put_1["name"]}', auth_lvl='ADMIN')
        self.assertEqual(response.status_code, 204)

        # Get deleted doctype
        response = self.get_request(f'/doctype/{tr.doctype_put_1["name"]}')
        self.assertEqual(response.status_code, 400)
        resp = json.loads(response.content)
        self.assertEqual(resp['error'], f"DocType ({tr.doctype_put_1['name']}) does not exist.")


    def test_approvalmatrix(self):
        # Load needed roles
        response = self.post_request('/role/', tr.role_post_1, auth_lvl='ADMIN')
        self.assertEqual(response.status_code, 201)        
        response = self.post_request('/role/', tr.role_post_2, auth_lvl='ADMIN')
        self.assertEqual(response.status_code, 201)        
        response = self.post_request('/role/', tr.role_post_3, auth_lvl='ADMIN')
        self.assertEqual(response.status_code, 201)
        # Load needed Departments
        response = self.post_request('/dept/', tr.dept_post_0, auth_lvl='ADMIN')
        self.assertEqual(response.status_code, 201)        
        response = self.post_request('/dept/', tr.dept_post_2, auth_lvl='ADMIN')
        self.assertEqual(response.status_code, 201)        
        response = self.post_request('/dept/', tr.dept_post_3, auth_lvl='ADMIN')
        self.assertEqual(response.status_code, 201)
        # Load needed Doc Types
        response = self.post_request('/doctype/', tr.doctype_post_1, auth_lvl='ADMIN')
        self.assertEqual(response.status_code, 201)        
        response = self.post_request('/doctype/', tr.doctype_post_2, auth_lvl='ADMIN')
        self.assertEqual(response.status_code, 201)        
        response = self.post_request('/doctype/', tr.doctype_post_3, auth_lvl='ADMIN')
        self.assertEqual(response.status_code, 201)

        am_ids = []
        response = self.post_request('/approvalmatrix/', tr.approvalmatrix_post_1, auth_lvl='USER')
        self.assert_auth_error(response, 'PERM_DENIED')

        response = self.post_request('/approvalmatrix/', tr.approvalmatrix_post_1, auth_lvl='ADMIN')
        self.assertEqual(response.status_code, 201)
        resp = json.loads(response.content)
        am_ids.append(resp['id'])
        
        response = self.post_request('/approvalmatrix/', tr.approvalmatrix_post_2, auth_lvl='ADMIN')
        self.assertEqual(response.status_code, 201)
        resp = json.loads(response.content)
        am_ids.append(resp['id'])
        
        response = self.post_request('/approvalmatrix/', tr.approvalmatrix_post_3, auth_lvl='ADMIN')
        self.assertEqual(response.status_code, 201)
        resp = json.loads(response.content)
        am_ids.append(resp['id'])

        # Duplicate
        response = self.post_request('/approvalmatrix/', tr.approvalmatrix_post_1, auth_lvl='ADMIN')
        self.assertEqual(response.status_code, 400)
        resp = json.loads(response.content)
        self.assertIn('The fields doc_type, department must make a unique set.', str(response.content))

        # List all approvalmatrixs with 'Op' in dept
        response = self.get_request('/approvalmatrix/?search=Ops')
        self.assertEqual(response.status_code, 200)
        resp = json.loads(response.content)
        resp['results'] = self.delete_list_attribs(resp['results'], ['id'])
        expected = self.paginate_results([tr.approvalmatrix_post_2, tr.approvalmatrix_post_3])
        self.assertEqual(resp, expected)

        # Error: Update approvalmatrix with signRoles as an object (not a str)
        response = self.put_request(f'/approvalmatrix/{am_ids[0]}', tr.approvalmatrix_put_err_1, auth_lvl='ADMIN')
        self.assertEqual(response.status_code, 400)
        self.assert_schema_err(response.content, 'signRoles')

        # Error: Update approvalmatrix with BadDocType
        response = self.put_request(f'/approvalmatrix/{am_ids[0]}', tr.approvalmatrix_put_err_2, auth_lvl='ADMIN')
        self.assertEqual(response.status_code, 400)
        resp = json.loads(response.content)
        self.assertEqual(resp['error'], 'Document Type: BadDocType does not exist.')

        # Error: Update approvalmatrix with BadDept
        response = self.put_request(f'/approvalmatrix/{am_ids[0]}', tr.approvalmatrix_put_err_3, auth_lvl='ADMIN')
        self.assertEqual(response.status_code, 400)
        resp = json.loads(response.content)
        self.assertEqual(resp['error'], 'Department: BadDept does not exist.')

        # Error: Update approvalmatrix with BadRole
        response = self.put_request(f'/approvalmatrix/{am_ids[0]}', tr.approvalmatrix_put_err_4, auth_lvl='ADMIN')
        self.assertEqual(response.status_code, 400)
        resp = json.loads(response.content)
        self.assertEqual(resp['error'], 'Role: BadRole does not exist.')

        # Update approvalmatrix
        response = self.put_request(f'/approvalmatrix/{am_ids[0]}', tr.approvalmatrix_put_1, auth_lvl='ADMIN')
        self.assertEqual(response.status_code, 200)

        # Get updated approvalmatrix
        response = self.get_request(f'/approvalmatrix/{am_ids[0]}')
        self.assertEqual(response.status_code, 200)
        resp = json.loads(response.content)
        resp = self.delete_attribs(resp, ['id'])
        self.assertEqual(resp, tr.approvalmatrix_put_1)

        # Error: permissions
        response = self.delete_request(f'/approvalmatrix/{am_ids[0]}')
        self.assert_auth_error(response, 'NO_AUTH')
        response = self.delete_request(f'/approvalmatrix/{am_ids[0]}', auth_lvl='USER')
        self.assert_auth_error(response, 'PERM_DENIED')

        # Delete updated approvalmatrix
        response = self.delete_request(f'/approvalmatrix/{am_ids[0]}', auth_lvl='ADMIN')
        self.assertEqual(response.status_code, 204)

        # Get deleted approvalmatrix
        response = self.get_request(f'/approvalmatrix/{am_ids[0]}')
        self.assertEqual(response.status_code, 400)
        resp = json.loads(response.content)
        self.assertEqual(resp['error'], f"ApprovalMatrix ({am_ids[0]}) does not exist.")

        