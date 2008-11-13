# zope imports
from zope.annotation.interfaces import IAnnotations
from BTrees.OOBTree import OOBTree

# Quills imports
from quills.app.portlets import tagcloud
from quills.app.portlets import weblogadmin
from quills.app.portlets import authors
from quills.app.portlets import recententries
from quills.app.portlets import quillslinks
from quills.app.portlets import recentcomments
from quills.app.portlets import archive

# plone imports
from plone.portlets.constants import CONTEXT_ASSIGNMENT_KEY, CONTEXT_CATEGORY
from plone.app.portlets.storage import PortletAssignmentMapping


DEFAULT_LEFT_PORTLETS = (
    ('tagcloud', tagcloud.Assignment, {}),
    ('archive', archive.Assignment, {}),
    ('quillslinks', quillslinks.Assignment, {}),
    )
DEFAULT_RIGHT_PORTLETS = (
    ('weblogadmin', weblogadmin.Assignment, {}),
    ('recententries', recententries.Assignment, {}),
    ('recentcomments', recentcomments.Assignment, {}),
    ('authors', authors.Assignment, {}),
    )


def registerContextPortlets(obj, event):
    """ An event listener that creates portlets assignments on context on blog creation
    """
    annotated = IAnnotations(obj)
    portlets = annotated.get(CONTEXT_ASSIGNMENT_KEY, OOBTree())

    left_portlets = portlets.get('plone.leftcolumn', PortletAssignmentMapping())
    right_portlets = portlets.get('plone.rightcolumn', PortletAssignmentMapping())

    for name, assignment, kwargs in DEFAULT_LEFT_PORTLETS:
        if not left_portlets.has_key(name):
            left_portlets[name] = assignment(**kwargs)
    for name, assignment, kwargs in DEFAULT_RIGHT_PORTLETS:
        if not right_portlets.has_key(name):
            right_portlets[name] = assignment(**kwargs)

    portlets['plone.leftcolumn'] = left_portlets
    portlets['plone.rightcolumn'] = right_portlets
    annotated[CONTEXT_ASSIGNMENT_KEY] = portlets


