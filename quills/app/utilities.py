# Standard library imports
from types import ListType
from types import TupleType
from types import StringTypes
import re

# to workaround slice incompatibility in Zope 2
from sys import maxint

# Zope imports
from Acquisition import Explicit
from Acquisition import aq_parent

# Plone imports
from Products.CMFCore.interfaces import ISiteRoot

# Quills imports
from quills.core.interfaces import IWeblog
from quills.core.interfaces import IWeblogEnhanced
from quills.core.interfaces import IWeblogConfiguration
from quills.core.interfaces import IWeblogEntry


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


class QuillsMixin(object):
    """
    """

    def getWeblogContentObject(self):
        return recurseToInterface(self, (IWeblog, IWeblogEnhanced))

    def getWeblog(self):
        obj = self.getWeblogContentObject()
        if IWeblog.providedBy(obj):
            return obj
        return IWeblog(obj)


def getArchivePathFor(obj, weblog_content):
    """See IWeblogView.
    """
    # Handle published and getId either being an attribute on a catalog brain or
    # a method on a content object.
    id = getattr(obj, 'getId')
    if callable(id):
        id = id()
    published = getattr(obj, 'effective', None)
    if published is None:
        published = getattr(obj, 'getPublicationDate')
    if callable(published):
        published = published() 
    path = []
    weblog_config = IWeblogConfiguration(weblog_content)
    archive_format = weblog_config.archive_format
    if isinstance(archive_format, StringTypes):
        archive_format = archive_format.strip()
    if archive_format is not None and archive_format is not '':
        path.append(archive_format)
    path.append(published.strftime('%Y'))
    path.append(published.strftime('%m'))
    path.append(published.strftime('%d'))
    path.append(id)
    return path

def getArchiveURLFor(obj, weblog_content):
    """See IWeblogView.
    """
    archive_path = getArchivePathFor(obj, weblog_content)
    return '%s/%s' % (weblog_content.absolute_url(), '/'.join(archive_path))

def recurseToInterface(item, ifaces):
    """Recurse up the aq_chain until an object providing `iface' is found,
    and return that.
    """
    if not isinstance(ifaces, (ListType, TupleType)):
        ifaces = [ifaces]
    parent = item.aq_inner.aq_parent
    for iface in ifaces:
        if iface.providedBy(item):
            return item
    for iface in ifaces:
        if iface.providedBy(parent):
            return parent
    for iface in ifaces:
        if ISiteRoot.providedBy(parent):
            # Stop when we get to the portal root.
            return None
    return recurseToInterface(parent, ifaces)


talkback_url_extractor = re.compile("(.*)/talkback/\d+")

def talkbackURL(discussion_brain):
    """expects the brain of a discussion item and constructs a url for it.
    n.b. we're using a regex in order to allow for the string 'talkback' to appear
    in the url in other places, too.
    """
    url = discussion_brain.getURL()
    absolute_url = talkback_url_extractor.search(url).groups()[0]
    return "%s#%s" % (absolute_url, discussion_brain.id)

class BloggifiedCatalogResults(object):
    """Wrap the CatalogBrains of the given iterable collection into
       IWeblogEntry adapters. All the elemets of catalogBrain must be
       wrappable by the same adapter class for reasons of optimization!
    """

    # A cached instance of the IWeblogEntry adapter to be used for
    # wrapping the catalog brains.
    _adapter = None

    def __init__(self, results):
        self.context = results
        # Cache an instance of the IWeblogAdapter which is to be used
        # for wrapping the brains. On class level for now. This expects
        # that all instances passed to this class actually can be handled
        # by the same wrapper!
        if BloggifiedCatalogResults._adapter is None and len(results) > 0:
            BloggifiedCatalogResults._adapter = IWeblogEntry(results[0])
            BloggifiedCatalogResults._adapter.context = None

    def __iter__(self):
        def iter(seq):
            for brain in self.context:
                yield BloggifiedCatalogResults.wrap(brain)
            raise StopIteration
        return iter(self.context)


    def __getitem__(self, k):
        """Return the item a index k or the slice indicated by k,
           the former as a IWeblogEntry the latter as an instance
           of this class.
        """
        if isinstance(k, slice):
            # Work around pre Python 2 collection code in Zope 2,
            # namely Products.ZCatalog.Lazy. Those will break on
            # slices. Why cannot things be simple for once?
            theSlice = None
            if k.step is None and hasattr(self.context, '__getslice__'):
                start = k.start
                stop = k.stop
                if start is None:
                    start = 0
                if stop is None:
                    stop = maxint
                theSlice = self.context[start:stop]
            else:
                theSlice = self.context[k]
                
            return BloggifiedCatalogResults(theSlice)
        else:
            return BloggifiedCatalogResults.wrap(self.context[k])

    def __len__(self):
        return len(self.context)

    def __contains__(self, item):
        return item in self.context
            
    def wrap(brain):
        """Wrap a catalog brain within an IWeblogEntry adapter.
        
        The _adater attribute of this instance is expected to hold
        an appropriate adapter instance for copying!
        """
        # adapter must be pickable for copy.copy to work
        # from copy import copy
        # adapter = copy(BloggifiedCatalogResults._adapter)
        # adapter.context = brain
        adapter = BloggifiedCatalogResults._adapter.__class__(brain)
        # Restricted code might (alas, and will) access this adapter,
        # that's why we will need to acquire the users roles.
        # XXX: Remove calls to IWeblogEntry from page templates
        #      that do are not explicitly allowed to access it!
        return adapter.__of__(brain)
    
    wrap = staticmethod(wrap)
        
