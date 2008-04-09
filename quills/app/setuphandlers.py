# Standard library imports
from StringIO import StringIO

# Zope imports
from transaction import commit
from zope.component import getUtility

# Plone imports
from Products.CMFCore.utils import getToolByName
#from plone.portlets.constants import CONTENT_TYPE_CATEGORY
from plone.portlets.interfaces import IPortletManager
from plone.app.portlets.storage import PortletAssignmentMapping

# Quills imports
from quills.core.interfaces import IWeblog
from quills.core.interfaces import IWeblogEnhanced
from quills.app.portlets import tagcloud
from quills.app.portlets import weblogadmin
from quills.app.portlets import authors
from quills.app.portlets import recententries
from quills.app.portlets import quillslinks
from quills.app.portlets import recentcomments
from quills.app.portlets import archive
from quills.app.portlets.context import INTERFACE_CATEGORY


def setup_gs_profiles(portal, profiles, out):
    setup_tool = getToolByName(portal, 'portal_setup')
    for extension_id in profiles:
        try:
            setup_tool.runAllImportStepsFromProfile('profile-%s' % extension_id)
        except Exception, e:
            print >> out, "Error while trying to GS import %s (%s, %s)" \
                          % (extension_id, repr(e), str(e))
            raise

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

def weblogPortletSetup(portal,
                       out,
                       ifaces=[IWeblog, IWeblogEnhanced]):
    left_column  = getUtility(IPortletManager, name="plone.leftcolumn")
    right_column = getUtility(IPortletManager, name="plone.rightcolumn")
    try:
        left_category = left_column[INTERFACE_CATEGORY]
    except KeyError:
        left_column[INTERFACE_CATEGORY] = PortletAssignmentMapping()
        left_category = left_column[INTERFACE_CATEGORY]
    try:
        right_category = right_column[INTERFACE_CATEGORY]
    except KeyError:
        right_column[INTERFACE_CATEGORY] = PortletAssignmentMapping()
        right_category = right_column[INTERFACE_CATEGORY]
    #for iface in [IWeblog, IWeblogEnhanced]:

    ifid = IWeblog.__identifier__
    left_portlets = left_category.get(ifid, None)
    right_portlets = right_category.get(ifid, None)
    # It may be that it hasn't been created yet, so just to be safe:
    if left_portlets is None:
        left_category[ifid] = PortletAssignmentMapping()
        left_portlets = left_category[ifid]
    if right_portlets is None:
        right_category[ifid] = PortletAssignmentMapping()
        right_portlets = right_category[ifid]
    for name, assignment, kwargs in DEFAULT_LEFT_PORTLETS:
        if not left_portlets.has_key(name):
            left_portlets[name] = assignment(**kwargs)
    for name, assignment, kwargs in DEFAULT_RIGHT_PORTLETS:
        if not right_portlets.has_key(name):
            right_portlets[name] = assignment(**kwargs)
