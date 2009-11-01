# Zope imports
from zope.interface import implements

# CMF imports
from Products.CMFCore.utils import getToolByName

try:
    ## for Plone 4
    from Products.CMFCore.interfaces import IActionProvider
except ImportError:
    ## for Plone 3
    from Products.CMFCore.interfaces.portal_actions import ActionProvider as IActionProvider

class AcquiringActionProvider:

    implements(IActionProvider)

    def listActions(self, info=None, object=None):
        """ List all the actions defined by a provider.

        If 'object' is specified, object specific actions are included.

        The 'info' argument is deprecated and may be removed in a future
        version. If 'object' isn't specified, the method uses for backwards
        compatibility 'info.content' as object.

        Returns -- Tuple of ActionInformation objects (or Action mappings)
        """
        raise NotImplementedError

    def getActionObject(self, action):
        """Return the actions object or None if action doesn't exist.
        
        'action' is an action 'path' (e.g. 'object/view').
        
        Raises an ValueError exception if the action is of the wrong format.
        
        Permission -- Private
        
        Returns -- The actions object reference.
        """
        raise NotImplementedError

    def listActionInfos(self, action_chain=None, object=None, check_visibility=1,
                        check_permissions=1, check_condition=1, max=-1):
        """ List ActionInfo objects.

        'action_chain' is a sequence of action 'paths' (e.g. 'object/view').
        If specified, only these actions will be returned in the given order.

        If 'object' is specified, object specific Actions are included.

        If 'max' is specified, only the first max Actions are returned.

        Permission -- Always available (not publishable)

        Returns -- Tuple of ActionInfo objects
        """
        atool = getToolByName(self, 'portal_actions')
        factions = atool.listFilteredActionsFor(self.aq_parent)
        actions = []
        for key in factions.keys():
            # We filter out most of the categories of actions as these will
            # get added anyway, and we don't want duplicates.
            if key in ['object_tabs', 'object']:
                actions.extend(factions[key])
        # This is a bit hacky.  We step through the actions and remove the
        # 'Contents' one as Plone will automatically add that later.
        actions2 = []
        for action in actions:
            if action['title'] != "Contents":
                actions2.append(action)
        return actions2


    def getActionInfo(self, action_chain, object=None, check_visibility=0,
                      check_condition=0):
        """ Get an ActionInfo object specified by a chain of actions.

        Permission -- Always available

        Returns -- ActionInfo object
        """
        raise NotImplementedError
