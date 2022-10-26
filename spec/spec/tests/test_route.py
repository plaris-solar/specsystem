import copy, json, os
from django.conf import settings
from utils.test_utils import SpecTestCase
from . import conf_resources as conf
from . import spec_resources as spec

# TODO: test created pdf with PyPDF2 https://www.geeksforgeeks.org/working-with-pdf-files-in-python/ 
# Test page order, content, file not selected not in pdf

# TODO: To change setttings for specific test, use: https://docs.djangoproject.com/en/4.1/topics/testing/tools/#overriding-settings
# TODO: To test email output use: https://docs.djangoproject.com/en/4.1/topics/testing/tools/#email-services

class RouteTest(SpecTestCase):

    def test_submit(self):
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
        # Load spec for submission
        spec_ids = []
        response = self.post_request('/spec/', spec.spec_post_1, auth_lvl='USER')
        self.assertEqual(response.status_code, 201)
        resp = json.loads(response.content)
        resp_post_1 = resp
        spec_ids.append(resp['num'])

        # Add two files
        with open('spec/tests/test_files/Text1.docx', 'rb') as fp:
            response = self.post_binary_request(f'/file/{spec_ids[0]}/A', {'file':(fp, 'Text1.docx')},  auth_lvl='USER')
        self.assertEqual(response.status_code, 200)
        with open('spec/tests/test_files/file_one.txt', 'rb') as fp:
            response = self.post_binary_request(f'/file/{spec_ids[0]}/A', {'file':(fp, 'file_one.txt')},  auth_lvl='USER')
        self.assertEqual(response.status_code, 200)

        # Update spec - Add signers. Set file order and incl_pdf
        response = self.put_request(f'/spec/{spec_ids[0]}/A', spec.spec_put_2, auth_lvl='ADMIN')
        self.assertEqual(response.status_code, 200)

        # Submit: 


