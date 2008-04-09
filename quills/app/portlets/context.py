# zope imports
from zope.interface import implements
#from zope.interface import Interface
#from zope.component import adapts

# plone imports
from plone.portlets.interfaces import IPortletContext
from plone.app.portlets.portletcontext import ContentContext

# quills imports
from quills.core.interfaces import IBaseContent
from quills.core.interfaces import IWeblog
from quills.core.interfaces import IWeblogEnhanced


INTERFACE_CATEGORY = 'interface_category'


class WeblogAwarePortletContext(ContentContext):
    """
    """

    implements(IPortletContext)

    def globalPortletCategories(self, placeless=False):
        cats = super(WeblogAwarePortletContext, self).globalPortletCategories(placeless)
        #ifaces = self._getInterfaces()
        ifaces = [IWeblog,]
        for iface in ifaces:
            cats.append((INTERFACE_CATEGORY, iface.__identifier__))
        return cats
