import copy, json, os
from django.conf import settings
from utils.test_utils import SpecTestCase
from . import conf_resources as conf
from . import spec_resources as spec

class SpecTest(SpecTestCase):

    def test_spec(self):
        # Load needed roles
        response = self.post_request('/role/', conf.role_post_1, auth_lvl='ADMIN')
        self.assertEqual(response.status_code, 201)        
        response = self.post_request('/role/', conf.role_post_2, auth_lvl='ADMIN')
        self.assertEqual(response.status_code, 201)        
        response = self.post_request('/role/', conf.role_post_3, auth_lvl='ADMIN')
        self.assertEqual(response.status_code, 201)
        # Load needed Departments
        response = self.post_request('/dept/', conf.dept_post_0, auth_lvl='ADMIN')
        self.assertEqual(response.status_code, 201)        
        response = self.post_request('/dept/', conf.dept_post_2, auth_lvl='ADMIN')
        self.assertEqual(response.status_code, 201)        
        response = self.post_request('/dept/', conf.dept_post_3, auth_lvl='ADMIN')
        self.assertEqual(response.status_code, 201)
        # Load needed Doc Types
        response = self.post_request('/doctype/', conf.doctype_post_1, auth_lvl='ADMIN')
        self.assertEqual(response.status_code, 201)        
        response = self.post_request('/doctype/', conf.doctype_post_2, auth_lvl='ADMIN')
        self.assertEqual(response.status_code, 201)        
        response = self.post_request('/doctype/', conf.doctype_post_3, auth_lvl='ADMIN')
        self.assertEqual(response.status_code, 201)
        # Load needed Approval Matricies
        response = self.post_request('/approvalmatrix/', conf.approvalmatrix_post_1, auth_lvl='ADMIN')
        self.assertEqual(response.status_code, 201)
        response = self.post_request('/approvalmatrix/', conf.approvalmatrix_post_3, auth_lvl='ADMIN')
        self.assertEqual(response.status_code, 201)

        spec_ids = []

        response = self.post_request('/spec/', spec.spec_post_1)
        self.assert_auth_error(response, 'NO_AUTH')

        response = self.post_request('/spec/', spec.spec_post_1, auth_lvl='USER')
        self.assertEqual(response.status_code, 201)
        resp = json.loads(response.content)
        resp_post_1 = resp
        spec_ids.append(resp['num'])
        
        response = self.post_request('/spec/', spec.spec_post_2, auth_lvl='ADMIN')
        self.assertEqual(response.status_code, 201)
        resp = json.loads(response.content)
        spec_ids.append(resp['num'])

        # Error - title missing
        err_body = copy.deepcopy(spec.spec_post_1)
        err_body['title'] = None
        response = self.post_request('/spec/', err_body, auth_lvl='ADMIN')
        self.assertEqual(response.status_code, 400)
        self.assert_schema_err(response.content, 'title')

        # List all specs with first number
        response = self.get_request(f'/spec/?num={spec_ids[0]}')
        self.assertEqual(response.status_code, 200)
        resp = json.loads(response.content)
        resp['results'] = self.delete_list_attribs(resp['results'], ['created_by', 'create_dt', 'mod_ts', 'jira', 'anon_access', 'hist', 'watched'])
        post_1 = copy.deepcopy(spec.spec_post_1)
        post_1['num'] = spec_ids[0]
        post_1['ver'] = 'A'
        post_1['reason'] = 'Initial Version'
        post_1['sigs'] = [
            {'role': 'Op_Line1', 'signed_dt': None, 'from_am': True, 'spec_one': True, 'signer': None, 'delegate': None},
            {'role': 'Qual', 'signed_dt': None, 'from_am': True, 'spec_one': False, 'signer': None, 'delegate': None}
        ]
        post_1['approved_dt'] = None
        post_1['sunset_extended_dt'] = None
        self.assertEqual(resp, self.paginate_results([post_1]))

        # List all specs with first number
        response = self.get_request(f'/spec/{spec_ids[0]}')
        self.assertEqual(response.status_code, 200)
        resp = json.loads(response.content)
        resp['results'] = self.delete_list_attribs(resp['results'], ['created_by', 'create_dt', 'mod_ts', 'jira', 'anon_access', 'hist', 'watched'])
        self.assertEqual(resp, self.paginate_results([post_1]))

        # List all specs with 'Spec Creation' in title'
        response = self.get_request(f'/spec/?title=Spec%20Creation')
        self.assertEqual(response.status_code, 200)
        resp = json.loads(response.content)
        resp['results'] = self.delete_list_attribs(resp['results'], ['created_by', 'create_dt', 'mod_ts', 'jira', 'anon_access', 'hist', 'watched'])
        self.assertEqual(resp, self.paginate_results([post_1]))

        # List all specs with 'two' in keywords'
        response = self.get_request(f'/spec/?keywords=two')
        self.assertEqual(response.status_code, 200)
        resp = json.loads(response.content)
        resp['results'] = self.delete_list_attribs(resp['results'], ['created_by', 'create_dt', 'mod_ts', 'jira', 'anon_access', 'hist', 'watched'])
        post_2 = copy.deepcopy(spec.spec_post_2)
        post_2['num'] = spec_ids[1]
        post_2['ver'] = 'A'
        post_2['reason'] = 'Initial Version'
        post_2['sigs'] = []
        post_2['approved_dt'] = None
        post_2['sunset_extended_dt'] = None
        self.assertEqual(resp, self.paginate_results([post_2]))

        # List all specs with 'Draft' in state'
        response = self.get_request(f'/spec/?state=Draft')
        self.assertEqual(response.status_code, 200)
        resp = json.loads(response.content)
        resp['results'] = self.delete_list_attribs(resp['results'], ['created_by', 'create_dt', 'mod_ts', 'jira', 'anon_access', 'hist', 'watched'])
        self.assertEqual(resp, self.paginate_results([post_1, post_2]))

        # List all specs created by spec user
        response = self.get_request(f'/spec/?created_by={os.getenv("USER_USER")}')
        self.assertEqual(response.status_code, 200)
        resp = json.loads(response.content)
        resp['results'] = self.delete_list_attribs(resp['results'], ['created_by', 'create_dt', 'mod_ts', 'jira', 'anon_access', 'hist', 'watched'])
        self.assertEqual(resp, self.paginate_results([post_1]))

        # Error: Not logged in
        response = self.get_request(f'/spec/{spec_ids[0]}/A')
        self.assertEqual(response.status_code, 400)
        resp = json.loads(response.content)
        self.assertEqual(resp['error'], f"spec {spec_ids[0]}-A cannot read without logging in.")

        # Get first spec
        response = self.get_request(f'/spec/{spec_ids[0]}/A', auth_lvl='USER')
        self.assertEqual(response.status_code, 200)
        resp = json.loads(response.content)
        resp = self.delete_attribs(resp, ['created_by', 'create_dt', 'mod_ts', 'jira', 'anon_access', 'hist', 'watched'])
        self.assertEqual(resp, post_1)

        # Error: Update spec with title an object (not a string)
        response = self.put_request(f'/spec/{spec_ids[0]}/A', spec.spec_put_err_1, auth_lvl='ADMIN')
        self.assertEqual(response.status_code, 400)
        self.assert_schema_err(response.content, 'title')

        # Add a valid reference to the put body
        spec.spec_put_1['refs'] = [{'num':spec_ids[1], 'ver':'A'}]

        # Error: Update spec - change state w/o admin
        response = self.put_request(f'/spec/{spec_ids[0]}/A', spec.spec_put_1, auth_lvl='USER')
        self.assertEqual(response.status_code, 400)
        resp = json.loads(response.content)
        self.assertEqual(resp['error'], 'State changes via update can only be done by an administrator.')

        # Error: Update spec - change state w/o comment
        response = self.put_request(f'/spec/{spec_ids[0]}/A', spec.spec_put_err_2, auth_lvl='ADMIN')
        self.assertEqual(response.status_code, 400)
        resp = json.loads(response.content)
        self.assertEqual(resp['error'], 'State changes updates require a comment.')

        # Add two files for reposition on update
        with open('spec/tests/test_files/Text1.docx', 'rb') as fp:
            response = self.post_binary_request(f'/file/{spec_ids[0]}/A', {'file':(fp, 'Text1.docx')},  auth_lvl='USER')
        self.assertEqual(response.status_code, 200)
        with open('spec/tests/test_files/torch.jpg', 'rb') as fp:
            response = self.post_binary_request(f'/file/{spec_ids[0]}/A', {'file':(fp, 'torch.jpg')},  auth_lvl='USER')
        self.assertEqual(response.status_code, 200)

        # Update spec - change state to Active
        response = self.put_request(f'/spec/{spec_ids[0]}/A', spec.spec_put_1, auth_lvl='ADMIN')
        self.assertEqual(response.status_code, 200)
        resp = json.loads(response.content)
        self.assertEqual(resp['state'], 'Active')
        self.assertEqual(resp['create_dt'], resp_post_1['create_dt'])
        self.assertEqual(resp['created_by'], resp_post_1['created_by'])
        self.assertNotEqual(resp['mod_ts'], resp_post_1['mod_ts'])
        self.assertEqual(len(resp['hist']), 1)
        self.assertEqual(resp['hist'][0]['upd_by'], os.getenv("ADMIN_USER"))
        self.assertEqual(resp['hist'][0]['change_type'], 'Update')
        self.assertEqual(resp['hist'][0]['comment'], spec.spec_put_1['comment'])
        self.assertEqual(len(resp['files']), 2)
        self.assertEqual(resp['files'][0]['seq'], 1)
        self.assertEqual(resp['files'][0]['filename'], 'torch.jpg')
        self.assertEqual(resp['files'][0]['incl_pdf'], False)
        self.assertEqual(resp['files'][1]['seq'], 2)
        self.assertEqual(resp['files'][1]['filename'], 'Text1.docx')
        self.assertEqual(resp['files'][1]['incl_pdf'], True)
        self.assertEqual(resp['refs'], [{'num': 300001, 'ver': 'A'}])

        # Update spec - change state back to Draft to catch signer changes
        response = self.put_request(f'/spec/{spec_ids[0]}/A', spec.spec_put_2, auth_lvl='ADMIN')
        self.assertEqual(response.status_code, 200)
        resp = json.loads(response.content)
        self.assertEqual(resp['state'], 'Draft')
        self.assertEqual(len(resp['hist']), 2)
        self.assertEqual(resp['hist'][0]['upd_by'], os.getenv("ADMIN_USER"))
        self.assertEqual(resp['hist'][0]['change_type'], 'Update')
        self.assertEqual(resp['hist'][0]['comment'], spec.spec_put_2['comment'])
        self.assertEqual(resp['hist'][1]['upd_by'], os.getenv("ADMIN_USER"))
        self.assertEqual(resp['hist'][1]['change_type'], 'Update')
        self.assertEqual(resp['hist'][1]['comment'], spec.spec_put_1['comment'])
        self.assertEqual(len(resp['files']), 2)
        self.assertEqual(resp['refs'], [])
        self.assertEqual(resp['sigs'], 
            [{'role': conf.role_post_3['role'], 'signed_dt': None, 'from_am': True, 'spec_one': True, 'signer': None, 'delegate': None}, 
            {'role': conf.role_post_1['role'], 'signed_dt': None, 'from_am': True, 'spec_one': False, 'signer': os.getenv("USER_USER"), 'delegate': None},
            {'role': conf.role_post_2['role'], 'signed_dt': None, 'from_am': False, 'spec_one': True, 'signer': os.getenv("ADMIN_USER"), 'delegate': None}]
        )
        self.assertEqual(resp['jira'], "TEST-1")
        self.assertEqual(resp['jira_url'], f'{settings.JIRA_URI}/browse/TEST-1')

        # Update spec - change state to Active
        response = self.put_request(f'/spec/{spec_ids[0]}/A', spec.spec_put_1, auth_lvl='ADMIN')
        self.assertEqual(response.status_code, 200)

        # Error: Update spec - change state w/o admin
        response = self.put_request(f'/spec/{spec_ids[0]}/A', spec.spec_put_1, auth_lvl='USER')
        self.assertEqual(response.status_code, 400)
        resp = json.loads(response.content)
        self.assertEqual(resp['error'], 'Spec is not in Draft state. Cannot update.')

        # Error: permissions
        response = self.delete_request(f'/spec/{spec_ids[0]}/A')
        self.assert_auth_error(response, 'NO_AUTH')
        response = self.delete_request(f'/spec/{spec_ids[0]}/A', auth_lvl='USER')
        resp = json.loads(response.content)
        self.assertEqual(resp['error'], 'Spec is not in Draft state, it cannot be edited.')

        # Error: Create new revision - no reason
        response = self.post_request(f'/spec/{spec_ids[0]}/A', {}, auth_lvl='ADMIN')
        self.assertEqual(response.status_code, 400)
        self.assert_schema_err(response.content, 'reason')

        # Create new revision
        response = self.post_request(f'/spec/{spec_ids[0]}/A', spec.spec_revise_post_1, auth_lvl='ADMIN')
        self.assertEqual(response.status_code, 201)
        resp = json.loads(response.content)
        self.assertEqual(resp['ver'], 'B')
        self.assertEqual(resp['state'], 'Draft')
        self.assertEqual(resp['reason'], spec.spec_revise_post_1['reason'])
        self.assertNotEqual(resp['create_dt'], resp_post_1['create_dt'])
        self.assertNotEqual(resp['created_by'], resp_post_1['created_by'])
        self.assertNotEqual(resp['mod_ts'], resp_post_1['mod_ts'])

        # Delete updated spec
        response = self.delete_request(f'/spec/{spec_ids[0]}/B', auth_lvl='USER')
        self.assertEqual(response.status_code, 204)

        # Get deleted spec
        response = self.get_request(f'/spec/{spec_ids[0]}/B', auth_lvl='USER')
        self.assertEqual(response.status_code, 400)
        resp = json.loads(response.content)
        self.assertEqual(resp['error'], f'Spec ({spec_ids[0]}/B) does not exist.')

    def test_file(self):
        # Load needed roles
        response = self.post_request('/role/', conf.role_post_1, auth_lvl='ADMIN')
        self.assertEqual(response.status_code, 201)        
        response = self.post_request('/role/', conf.role_post_2, auth_lvl='ADMIN')
        self.assertEqual(response.status_code, 201)        
        response = self.post_request('/role/', conf.role_post_3, auth_lvl='ADMIN')
        self.assertEqual(response.status_code, 201)
        # Load needed Departments
        response = self.post_request('/dept/', conf.dept_post_0, auth_lvl='ADMIN')
        self.assertEqual(response.status_code, 201)        
        response = self.post_request('/dept/', conf.dept_post_2, auth_lvl='ADMIN')
        self.assertEqual(response.status_code, 201)        
        response = self.post_request('/dept/', conf.dept_post_3, auth_lvl='ADMIN')
        self.assertEqual(response.status_code, 201)
        # Load needed Doc Types
        response = self.post_request('/doctype/', conf.doctype_post_1, auth_lvl='ADMIN')
        self.assertEqual(response.status_code, 201)        
        response = self.post_request('/doctype/', conf.doctype_post_2, auth_lvl='ADMIN')
        self.assertEqual(response.status_code, 201)        
        response = self.post_request('/doctype/', conf.doctype_post_3, auth_lvl='ADMIN')
        self.assertEqual(response.status_code, 201)
        #Create Specs
        spec_ids = []
        response = self.post_request('/spec/', spec.spec_post_1, auth_lvl='USER')
        self.assertEqual(response.status_code, 201)
        resp = json.loads(response.content)
        resp_post_1 = resp
        spec_ids.append(resp['num'])        
        response = self.post_request('/spec/', spec.spec_post_2, auth_lvl='ADMIN')
        self.assertEqual(response.status_code, 201)
        resp = json.loads(response.content)
        spec_ids.append(resp['num'])

        # Error: Not logged in
        response = self.post_request(f'/file/{spec_ids[0]}/A', {})
        self.assert_auth_error(response, 'NO_AUTH')

        # Error: Missing file
        response = self.post_request(f'/file/{spec_ids[0]}/A', {},auth_lvl='USER')
        self.assertEqual(response.status_code, 400)
        self.assert_schema_err(response.content, 'file')

        # Upload Word file
        with open('spec/tests/test_files/Text1.docx', 'rb') as fp:
            response = self.post_binary_request(f'/file/{spec_ids[0]}/A', {'file':(fp, 'Text1.docx')},  auth_lvl='USER')
        self.assertEqual(response.status_code, 200)
        resp = json.loads(response.content)
        self.assertEqual(len(resp['files']), 1)
        self.assertEqual(resp['files'][0]['seq'], 1)
        self.assertEqual(resp['files'][0]['filename'], 'Text1.docx')
        self.assertEqual(resp['files'][0]['incl_pdf'], False)

        # Upload jpg file
        with open('spec/tests/test_files/torch.jpg', 'rb') as fp:
            response = self.post_binary_request(f'/file/{spec_ids[0]}/A', {'file':(fp, 'torch.jpg')},  auth_lvl='USER')
        self.assertEqual(response.status_code, 200)
        resp = json.loads(response.content)
        self.assertEqual(len(resp['files']), 2)
        self.assertEqual(resp['files'][0]['seq'], 1)
        self.assertEqual(resp['files'][0]['filename'], 'Text1.docx')
        self.assertEqual(resp['files'][0]['incl_pdf'], False)
        self.assertEqual(resp['files'][1]['seq'], 2)
        self.assertEqual(resp['files'][1]['filename'], 'torch.jpg')
        self.assertEqual(resp['files'][1]['incl_pdf'], False)

        # Upload txt file
        with open('spec/tests/test_files/file_one.txt', 'rb') as fp:
            response = self.post_binary_request(f'/file/{spec_ids[0]}/A', {'file':(fp, 'file_one.txt')},  auth_lvl='USER')
        self.assertEqual(response.status_code, 200)
        resp = json.loads(response.content)
        self.assertEqual(len(resp['files']), 3)
        self.assertEqual(resp['files'][0]['seq'], 1)
        self.assertEqual(resp['files'][0]['filename'], 'Text1.docx')
        self.assertEqual(resp['files'][0]['incl_pdf'], False)
        self.assertEqual(resp['files'][1]['seq'], 2)
        self.assertEqual(resp['files'][1]['filename'], 'torch.jpg')
        self.assertEqual(resp['files'][1]['incl_pdf'], False)
        self.assertEqual(resp['files'][2]['seq'], 3)
        self.assertEqual(resp['files'][2]['filename'], 'file_one.txt')
        self.assertEqual(resp['files'][2]['incl_pdf'], False)

        # Delete file
        response = self.delete_request(f'/file/{spec_ids[0]}/A/torch.jpg', auth_lvl='USER')
        self.assertEqual(response.status_code, 204)

        # Error: get deleted file
        response = self.get_request(f'/file/{spec_ids[0]}/A/torch.jpg', auth_lvl='USER')
        self.assertEqual(response.status_code, 400)
        resp = json.loads(response.content)
        self.assertEqual(resp['error'],  f"File torch.jpg is not attached to spec ({spec_ids[0]}/A).")

        # Get first file on spec
        response = self.get_request(f'/file/{spec_ids[0]}/A', auth_lvl='USER')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.filename,  'Text1.docx')

        # Get file by name
        with open('spec/tests/test_files/file_one.txt', 'rb') as fp:
            file_content = fp.read()
        response = self.get_request(f'/file/{spec_ids[0]}/A/file_one.txt', auth_lvl='USER')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.filename,  'file_one.txt')
        stream = b''.join(response.streaming_content)
        self.assertEqual(stream,  file_content)


