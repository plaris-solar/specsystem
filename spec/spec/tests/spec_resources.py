import os
from . import conf_resources as conf

spec_post_1 = {
    "title": "SOP, Spec Creation",
    "keywords": "keyword one",
    "doc_type": "SOP",
    "department": "Ops:Line1",
    "sigs": [],
    "files": [],
    "refs": [],
    "state":"Draft"
}

spec_post_2 = {
    "title": "WI, Route Spec",
    "keywords": "keyword two",
    "doc_type": "WI",
    "department": "Ops",
    "sigs": [],
    "files": [],
    "refs": [],
    "state":"Draft"
}

spec_revise_post_1 = {
    "reason": "Creating Rev B"
}

spec_put_1 = {
    "title": "SOP, Spec Creation",
    "keywords": "keyword one",
    "doc_type": "SOP",
    "department": "Ops:Line1",
    "sigs": [],
    "files": [{"filename":"torch.jpg", "incl_pdf":False}, {"filename":"Text1.docx", "incl_pdf":True}],
    "refs": [],
    "state":"Active",
    "comment": "Change state for testing"
}

spec_put_2 = {
    "title": "SOP, Spec Creation",
    "keywords": "keyword one",
    "doc_type": "SOP",
    "department": "Ops:Line1",
    "jira": "TEST-1",
    "sigs": [{'role':conf.role_post_1['role'],'signer':os.getenv("USER_USER"), 'from_am':True}, 
             {'role':conf.role_post_2['role'],'signer':os.getenv("ADMIN_USER"), 'from_am':False},
             {'role':conf.role_post_3['role'],'signer':None, 'from_am':True}],
    "files": [{"filename":"torch.jpg", "incl_pdf":False}, {"filename":"Text1.docx", "incl_pdf":True}],
    "refs": [],
    "state":"Draft",
    "comment": "Change state back to Draft for testing"
}

spec_put_err_1 = {
    "title": {},
    "keywords": "SPEC",
    "doc_type": "WI",
    "department": "Quality",
    "sigs": [],
    "files": [],
    "refs": []
}

spec_put_err_2 = {
    "title": "SOP, Spec Creation",
    "keywords": "keyword one",
    "doc_type": "SOP",
    "department": "Ops:Line1",
    "sigs": [],
    "files": [],
    "refs": [],
    "state":"Active"
}
