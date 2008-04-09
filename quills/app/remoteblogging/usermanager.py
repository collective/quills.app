# Zope imports
from zope.interface import implements

# CMF imports
from Products.CMFCore.utils import getToolByName

# Local imports
from quills.remoteblogging.interfaces import IUIDManager, IUserManager


USER_INFO = {
    'name'      : 'no name',
    'email'     : 'no email',
    'userid'    : 'no user id',
    'firstname' : 'no first name',
    'lastname'  : 'no last name',
    'url'       : 'no url',
    }


class WeblogUserManager:
    """
    >>> from zope.interface.verify import verifyClass
    >>> verifyClass(IUserManager, WeblogUserManager)
    True
    """

    implements(IUserManager)
    
    def __init__(self, context):
        self.context = context

    def getWeblogsForUser(self, user_id):
        """See IUserManager.
        """
        # This method returns a list with details for *only* the weblog that is
        # being adapted here.
        parent_blog = self.context
        blogs = []
        blogs.append(
            {'url': self.context.absolute_url(),
             'blogid' : IUIDManager(self.context).getUID(),
             'blogName' : self.context.Title(),
            }
            )
        return blogs

    def getUserInfo(self, user_id):
        """See IUserManager.
        """
        membership = getToolByName(self.context, 'portal_membership')
        info = USER_INFO.copy()
        member = membership.getAuthenticatedMember()
        if member:
            for key,value in info.items():
                info[key] = getattr(member, key, None) or value
        return info


class PortalUserManager:

    implements(IUserManager)

    def __init__(self, context):
        self.context = context

    def getWeblogsForUser(self, user_id):
        """See IUserManager.
        """
        # This method returns a list with details for all weblogs within the
        # portal.
        catalog = getToolByName(self.context, 'portal_catalog')
        results = catalog(meta_type='Weblog', Creator=user_id)
        blogs = []
        for item in results:
            obj = item.getObject()
            blogs.append(
                    {'url': obj.absolute_url(),
                     'blogid' : IUIDManager(obj).getUID(),
                     'blogName' : obj.Title()
                     }
                        )
        return blogs

    def getUserInfo(self, user_id):
        """See IUserManager.
        """
        membership = getToolByName(self.context, 'portal_membership')
        info = USER_INFO.copy()
        member = membership.getAuthenticatedMember()
        if member:
            for key,value in info.items():
                info[key] = getattr(member, key, None) or value
        return info
