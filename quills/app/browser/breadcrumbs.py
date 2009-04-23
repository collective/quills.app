from Acquisition import aq_base
from Products.CMFPlone.browser.interfaces import INavigationBreadcrumbs
from quills.core.interfaces import IBaseContent, IWeblogEntry, IWeblogEnhanced
from zope.component import getMultiAdapter
from zope.interface import implements


class ArchiveAwareBreadcrumbs(object):
    """Workaround ATContentTypes' habit to use the inner acquisition chain
    for building the breadcrumbs. This would make the archive path disapear.
    """

    implements(INavigationBreadcrumbs)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def breadcrumbs(self):
        """This method should return a tuple of the form:

            ({'absolute_url': url_value,
                     'Title': title_value,
             },)
        """
        base = getMultiAdapter((self.container(),
                                self.request), name='breadcrumbs_view')
        crumbs = tuple(base.breadcrumbs())
        crumbs += ({'absolute_url': self.context.absolute_url(),
                   'Title': IWeblogEntry(self.context).getTitle(),
                   },)
        return crumbs

    def container(self):
        """Return the container of the WeblogEntry the breadcrumbs lead to.
        
        The previous implemention tried to skip over unwanted objects in the
        parent stack. Now and then something new turned up and broke the
        breadcrumbs (e.g. issue #179). This implemention will look for
        something we know. This is still a bad hack, but more reliable and
        a bit easier to grasp than the former (so I hope).
        """
        for parent in self.request['PARENTS']:
            if ((IBaseContent.providedBy(parent) or
                  IWeblogEnhanced.providedBy(parent))
                and aq_base(parent) != aq_base(self.context)):
                return parent
        # Just in case. We would probably better raise an exception here.
        return None
