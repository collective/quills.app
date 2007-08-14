# Standard library imports
from types import StringTypes

# Zope 3 imports
from zope.interface import implements
from zope.component import getUtility

# Zope 2 imports
from Acquisition import Implicit, aq_base
from OFS.Traversable import Traversable

# CMF imports
from Products.CMFCore.utils import getToolByName

# Plone imports
from plone.i18n.normalizer.interfaces import IIDNormalizer

# Product imports
from quills.core.interfaces import ITopic, IAuthorTopic
from acquiringactions import AcquiringActionProvider
from weblogentrybrain import WeblogEntryCatalogBrain
from utilities import WeblogFinder, EvilAATUSHack


class Topic(WeblogFinder, AcquiringActionProvider, Traversable, Implicit):
    """Implementation of ITopic as a transient wrapper around a keywords.
    """

    implements(ITopic)

    __allow_access_to_unprotected_subobjects__ = EvilAATUSHack()

    def __init__(self, keywords):
        if isinstance(keywords, StringTypes):
            self.keywords = [keywords,]
        else:
            self.keywords = keywords
        # We will cache catalog queries for performance reasons.
        # This should not cost anything (except a bit of RAM) as Topic instances
        # only last for the duration of a REQUEST anyway.
        self.results = None

    def getId(self):
        """See ITopic.
        """
        return self.keywords[0]

    def getTitle(self):
        """See ITopic.
        """
        image = self.getImage()
        if image is not None:
            return image.Title()
        return self.getId()

    #def title_or_id(self):
    #    """See ITopic.
    #    """
    #    image = self.getImage()
    #    if image is not None:
    #        return image.title_or_id()
    #    return self.getId()

    def getDescription(self):
        """See ITopic.
        """
        image = self.getImage()
        if image is not None:
            return image.Description()
        return ''

    def getImage(self):
        """See ITopic.
        """
        # N.B. 'topic_images' is acquired here, if necessary.  This means
        # that you can have a single 'topic_images' folder serving multiple
        # weblog instances.
        topic_images = getattr(self, 'topic_images', None)
        if topic_images is None:
            return None
        normalizer = getUtility(IIDNormalizer)
        keyword_id = normalizer.normalize(self.keywords[0])
        # To check for the presence of the image, we want to limit ourselves to
        # unacquired objects, so we use aq_base.
        image = getattr(aq_base(topic_images), keyword_id, None)
        if image is not None:
            # Now we've found it, we want to pass back an Implicit wrapper,
            # so we lookup the object again.
            image = getattr(topic_images, keyword_id)
        else:
            # Fallback for older Quills releases which did not normalize
            # the keyword to a safe Zope id.
            # Again, limit to unacquired objects
            image = getattr(aq_base(topic_images), self.keywords[0], None)
            if image is not None:
                # And then get the Implicit wrapper
                image = getattr(topic_images, self.keywords[0])
        return image

    def getEntries(self):
        """See ITopic.
        """
        weblog = self.getParentWeblog()
        path = '/'.join(weblog.getPhysicalPath())
        catalog = getToolByName(self, 'portal_catalog')
        catalog._catalog.useBrains(WeblogEntryCatalogBrain)
        results = catalog(meta_type='WeblogEntry',
                path={'query':path, 'level': 0},
                Subject={'query'    : self.keywords,
                         'operator' : 'and'},
                sort_on='effective',
                sort_order='reverse',
                review_state='published')
        return results

    def __str__(self):
        """See ITopic.
        """
        return self.keywords[0]

    def __len__(self):
        """See ITopic.
        """
        return len(self.getEntries())


class AuthorTopic(Topic):
    """
    """

    implements(IAuthorTopic)

    def getTitle(self):
        """See ITopic.
        """
        memb_tool = getToolByName(self, 'portal_membership')
        return memb_tool.getMemberInfo(self.keywords[0])['fullname']


    #def title_or_id(self):
    #    """See ITopic.
    #    """
    #    memb_tool = getToolByName(self, 'portal_membership')
    #    title = memb_tool.getMemberInfo(self.keywords[0])['fullname']
    #    if title:
    #        return title
    #    return self.getId()

    def getDescription(self):
        """See ITopic.
        """
        # XXX Fix me with something sensible.
        # Get the description from the member object?
        return ''

    def getImage(self):
        """See ITopic.
        """
        memb_tool = getToolByName(self, 'portal_membership')
        return memb_tool.getPersonalPortrait(self.keywords[0])

    def getEntries(self):
        """See ITopic.
        """
        weblog = self.getParentWeblog()
        path = '/'.join(weblog.getPhysicalPath())
        catalog = getToolByName(self, 'portal_catalog')
        catalog._catalog.useBrains(WeblogEntryCatalogBrain)
        results = catalog(meta_type='WeblogEntry',
                path={'query':path, 'level': 0},
                Creator={'query'    : self.keywords,
                         'operator' : 'or'},
                sort_on='effective',
                sort_order='reverse',
                review_state='published')
        return results
