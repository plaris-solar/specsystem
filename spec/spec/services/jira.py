from jira import JIRA
from django.conf import settings
from rest_framework.exceptions import ValidationError

# There is no unit testing of this module, because JIRA is an external system. 
# And the setup requires access and an existing ticket configured

def conn(): # pragma nocover
    if settings.JIRA_URI is None or len(settings.JIRA_URI) == 0:
        return None
    try:
        return JIRA(settings.JIRA_URI, basic_auth=(settings.JIRA_USER, settings.JIRA_TOKEN))
    except BaseException as be:
        raise ValidationError({"errorCode":"SPEC-J01", "error": f"Error connecting to Jira. URL:{settings.JIRA_URI}, User: {settings.JIRA_USER}, Error: {be}"})

def create(spec): # pragma nocover
    """If Document Type has a Jira issue listed, clone that issue and its children for this spec"""
    jira = conn()
    if jira is None:
        return None

    if spec.doc_type.jira_temp is None or len(spec.doc_type.jira_temp) == 0:
        return None
    
    try:
        temp_issue = jira.issue(spec.doc_type.jira_temp)
        new_issue = jira.create_issue(
            project=settings.JIRA_PROJ, 
            summary=f'{spec.num}-{spec.ver}: ' + temp_issue.fields.summary, 
            description=temp_issue.fields.description, 
            issuetype={'name':temp_issue.fields.issuetype.name},
            labels=[f'{spec.num}-{spec.ver}'],
            )
        spec.jira = new_issue.key
        spec.save()

        for iss in temp_issue.fields.subtasks:
            st = jira.issue(iss.key)
            new_subtask = jira.create_issue(
                project=settings.JIRA_PROJ, 
                parent={'key':spec.jira}, 
                summary=f'{spec.num}-{spec.ver}: ' + st.fields.summary, 
                description=st.fields.description, 
                issuetype={'name':st.fields.issuetype.name},
                labels=[f'{spec.num}-{spec.ver}'],
                )            

    except BaseException as be:
        raise ValidationError({"errorCode":"SPEC-J02", "error": f"Error creating Jira issue from {spec.doc_type.jira_temp}, Error: {be}"})
    

def submit(spec): # pragma nocover
    """Update the state of related Jira Tasks to Signoff"""
    jira = conn()
    if jira is None:
        return None

    if spec.jira is None or len(spec.jira) == 0:
        return None

    try:
        jira_issue = jira.issue(spec.jira)
        substasks = []
        errors = []

        if jira_issue.fields.status.name != 'Signoff': 
            if jira_issue.fields.status.name != 'Draft':
                errors.append(f"Jira issue {jira_issue.key} is in status {jira_issue.fields.status.name}, not Draft.")
   
        for iss in jira_issue.fields.subtasks:
            st = jira.issue(iss.key)            
            if st.fields.status.name == 'N/A':
                continue
            if st.fields.assignee is None:
                errors.append(f"Jira issue {st.key} does not have an assignee.")
            if st.fields.status.name == 'Signoff':
                continue
            if st.fields.status.name != 'Draft':
                errors.append(f"Jira issue {st.key} is in status {st.fields.status.name}, not Draft.")
            substasks.append(st)
        
        if len(errors) > 0:
            raise Exception(f"Error(s): {'; '.join(errors)}")

        for st in substasks:
            jira.transition_issue(st, transition='Submit')
        jira.transition_issue(jira_issue, transition='Submit')

    except BaseException as be:
        raise ValidationError({"errorCode":"SPEC-J03", "error": f"Error transitioning Jira issue {spec.jira} to Submit, Error: {be}"})

def reject(spec): # pragma nocover
    """Update the state of related Jira Tasks to Draft"""
    jira = conn()
    if jira is None:
        return None

    if spec.jira is None or len(spec.jira) == 0:
        return None

    try:
        jira_issue = jira.issue(spec.jira)
        if jira_issue.fields.status.name != 'Draft': 
            if jira_issue.fields.status.name != 'Signoff':
                raise Exception(f"Error: Jira issue {jira_issue.key} is in status {jira_issue.fields.status.name}, not Signoff.")
            jira.transition_issue(jira_issue, transition='Reject')

        for iss in jira_issue.fields.subtasks:
            st = jira.issue(iss.key)
            if st.fields.status.name == 'N/A':
                continue
            if st.fields.status.name == 'Draft':
                continue
            if st.fields.status.name != 'Signoff':
                raise Exception(f"Error: Jira issue {st.key} is in status {st.fields.status.name}, not Signoff.")
            jira.transition_issue(st, transition='Reject')

    except BaseException as be:
        raise ValidationError({"errorCode":"SPEC-J03", "error": f"Error transitioning Jira issue {spec.jira} to Draft, Error: {be}"})

def active(spec): # pragma nocover
    """Update the state of related Jira Tasks to In Progress"""
    jira = conn()
    if jira is None:
        return None

    if spec.jira is None or len(spec.jira) == 0:
        return None

    try:
        jira_issue = jira.issue(spec.jira)
        if jira_issue.fields.status.name != 'In Process': 
            if jira_issue.fields.status.name != 'Signoff':
                raise Exception(f"Error: Jira issue {jira_issue.key} is in status {jira_issue.fields.status.name}, not Signoff.")
            jira.transition_issue(jira_issue, transition='Approve')

        for iss in jira_issue.fields.subtasks:
            st = jira.issue(iss.key)
            if st.fields.status.name == 'N/A':
                continue
            if st.fields.status.name == 'In Process':
                continue
            if st.fields.status.name != 'Signoff':
                raise Exception(f"Error: Jira issue {st.key} is in status {st.fields.status.name}, not Signoff.")
            jira.transition_issue(st, transition='Approve')

    except BaseException as be:
        raise ValidationError({"errorCode":"SPEC-J03", "error": f"Error transitioning Jira issue {spec.jira} to Draft, Error: {be}"})

def delete(spec): # pragma nocover
    """Delete the Jira Tasks"""
    jira = conn()
    if jira is None:
        return None

    if spec.jira is None or len(spec.jira) == 0:
        return None

    try:
        jira_issue = jira.issue(spec.jira)

        for iss in jira_issue.fields.subtasks:
            st = jira.issue(iss.key)
            st.delete()         
        jira_issue.delete()
        spec.jira = None
        spec.save()

    except BaseException as be:
        raise ValidationError({"errorCode":"SPEC-J06", "error": f"Error deleting Jira issue {spec.jira}, Error: {be}"})
