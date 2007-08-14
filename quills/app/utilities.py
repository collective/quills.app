# Zope imports
from Acquisition import aq_base, aq_parent, Explicit
from Products.ZCatalog.CatalogBrains import AbstractCatalogBrain

# Plone imports
from Products.CMFCore.interfaces import ISiteRoot

# Quills imports
from quills.core.interfaces import IWeblog, IWeblogViewConfiguration


class EvilAATUSHack(Explicit):

    def __call__(self, name, value):
        """Deny access to attributes that are found on the class or instance,
        but allow access to anything else.  This locks down security on object
        attributes, but allows the lookup of portlets with the 'provider'
        TAL command.
        """
        context = aq_parent(self)
        idict = context.__dict__
        cdict = context.__class__.__dict__
        if idict.has_key(name) or cdict.has_key(name):
            return 0
        return 1


class WeblogFinder:
    
    def getParentWeblog(self, item=None):
        """Recurse up the aq_chain until an IWeblog is found, and return that.
        """
        if item is None:
            # Make it so that this method can be used from a view/adapter, as
            # well as directly on a content object that subclasses WeblogFinder.
            if hasattr(aq_base(self), 'context'):
                item = self.context
            else:
                item = self
        if isinstance(item, AbstractCatalogBrain):
            # We need to get hold of the actual WeblogEntry and then acquire its
            # parent weblog.  This implies a bit of a performance hit, and it's
            # unclear that Topics and Authors really *need* to be returned in
            # the context of the IWeblog.  That's just how it's done elsewhere
            # in the codebase at the moment.
            item = item.getObject()
        parent = item.aq_parent
        if IWeblog.providedBy(item):
            return item
        elif IWeblog.providedBy(parent):
            return parent
        elif ISiteRoot.providedBy(parent):
            # Stop when we get to the portal root.
            return None
        else:
            return self.getParentWeblog(parent)


def getArchivePathFor(obj, weblog=None):
    """See IWeblogView.
    """
    # Handle published and getId either being an attribute on a catalog brain or
    # a method on a content object.
    id = getattr(obj, 'getId')
    if callable(id):
        id = id()
    published = getattr(obj, 'effective')
    if callable(published):
        published = published()
    path = []
    if weblog is None:
        # XXX This is a bit hacky! Should probably lookup a view here.
        weblog = WeblogFinder().getParentWeblog(obj)
    weblog_config = IWeblogViewConfiguration(weblog)
    archive_format = weblog_config.archiveFormat
    if archive_format is not '':
        path.append(archive_format)
    path.append(published.strftime('%Y'))
    path.append(published.strftime('%m'))
    path.append(published.strftime('%d'))
    path.append(id)
    return path

def getArchiveURLFor(weblog, obj):
    """See IWeblogView.
    """
    archive_path = getArchivePathFor(obj, weblog)
    return '%s/%s' % (weblog.absolute_url(), '/'.join(archive_path))

