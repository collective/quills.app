# zope imports
from zope.interface import implements

# CMF imports
from Products.CMFCore.utils import getToolByName

# Local imports
from quills.remoteblogging.interfaces import IUIDManager


class UIDManager:
    """
    >>> from zope.interface.verify import verifyClass
    >>> verifyClass(IUIDManager, UIDManager)
    True
    """

    implements(IUIDManager)

    def __init__(self, context):
        self.context = context

    def getByUID(self, uid):
        """See IUIDManager.
        """
        if uid=='0' or uid=='' or uid is None:
            return self.context
        uid_catalog = getToolByName(self.context, 'uid_catalog')
        lazy_cat = uid_catalog(UID=uid)
        if len(lazy_cat)>0:
            obj = lazy_cat[0].getObject()
            return obj
        else:
            return self.context

    def getUIDFor(self, obj):
        """See IUIDManager.
        """
        if obj is None:
            obj = self.context
        uid = getattr(obj, 'UID', None)
        if uid is None:
            # XXX A bit hacky! This is for the case where obj is an adapter
            # (i.e. in QuillsEnabled). It may make sense to refactor this so
            # that IWeblogEntry has a getUID method, although that seems rather
            # heavy-handed given that IWeblogEntry has no real reason to have
            # that method, other than to support remote blogging.
            uid = getattr(obj.context, 'UID')
        if callable(uid):
            return uid()
        return uid

    def getUID(self):
        """See IUIDManager.
        """
        return self.getUIDFor(self.context)
