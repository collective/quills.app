from zope.interface import implements
from zope.component import getUtility
from Products.CMFCore.interfaces import ISiteRoot
from quills.core.interfaces import IWeblogEnhanced
from quills.core.interfaces import IWeblog
from quills.app.utilities import recurseToInterface
from quills.app.traversal import IInsideWeblog
from quills.core.interfaces import IWeblogLocator


class RecursingUpLocator(object):
    """see Interface, recurses up"""
    implements(IWeblogLocator)
    
    def __init__(self, context):
        self.context = context
        
    def find(self):
        """see Interface"""
        # The request tells us if were inside a weblog; if we are
        # not, we leave immediately. --- jhackel
        request = getattr(self.context, 'request', None)
        if not ( request is None or IInsideWeblog.providedBy(request) ):
            return []

        weblog_content = recurseToInterface(self.context.aq_inner,
                                            (IWeblog, IWeblogEnhanced))
        if weblog_content is None:
            return []
        return IWeblog(weblog_content)

class SelfLocator(object):
    """see Interface, takes always the context itself."""
    implements(IWeblogLocator)
    
    def __init__(self, context):
        self.context = context
        
    def find(self):
        """see Interface"""
        assert(IWeblog.providedBy(self.context)) 
        return self.context



class LatestFromCatalogLocator(object):
    """see Interface, uses the catalog."""
    implements(IWeblogLocator)
    
    def __init__(self, context):
        self.context = context
        
    def find(self):
        """see Interface"""
        site = getUtility(ISiteRoot, context=self.context)
        catalog = site.portal_catalog
        query = {
            'object_provides': 'quills.core.interfaces.weblog.IWeblog',
            'sort_on': 'effective',
            'sort_order': 'reverse',
        }
        result = catalog(**query)
        if len(result) == 0:
            return []
        return result[0].getObject()
