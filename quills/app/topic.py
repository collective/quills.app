# -*- coding: utf-8 -*-
""" 
XXX TODO
--------
    
- Topics containing multiple keywords do not work properly: 
  - Neither author nor keyword topics can return multiple
    images as would be required when filtering by multiple 
    keywords/authors --- jhackel
"""

# Standard library imports
from types import StringTypes

# Zope 3 imports
from zope.interface import implements
from zope.component import getUtility
from zope.component.interface import interfaceToName

# Zope 2 imports
from Acquisition import Implicit, aq_base
from OFS.Traversable import Traversable

# CMF imports
from Products.CMFCore.utils import getToolByName

# Plone imports
from plone.i18n.normalizer.interfaces import IIDNormalizer

# Quills imports
from quills.core.interfaces import ITopic
from quills.core.interfaces import IAuthorTopic
from quills.core.interfaces import ITopicContainer
from quills.core.interfaces import IAuthorContainer
from quills.core.interfaces import IWeblogEntry
from quills.core.interfaces import IPossibleWeblogEntry
from acquiringactions import AcquiringActionProvider
from utilities import BloggifiedCatalogResults
from utilities import EvilAATUSHack
from utilities import QuillsMixin
from interfaces import ITransientTopicContainer
from interfaces import ITransientAuthorContainer
from interfaces import IWeblogEnhancedConfiguration


class Topic(QuillsMixin, AcquiringActionProvider, Traversable, Implicit):
    """Implementation of ITopic as a transient wrapper around a keywords.

    >>> from zope.interface.verify import verifyClass
    >>> verifyClass(ITopic, Topic)
    True
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

    def getKeywords(self):
        """See ITopic.
        """
        # Return a copy so they can't be changed by other code.
        return self.keywords[:]

    def getTitle(self):
        """See ITopic.
        """
        return ' & '.join(self.keywords).decode('utf-8')

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
        # XXX: Behaves awkwardly for multiple keyword topics. The
        # keyword will determine the image.

        # N.B. 'topic_images' is acquired here, if necessary.  This means
        # that you can have a single 'topic_images' folder serving multiple
        # weblog instances.
        topic_images = getattr(self, 'topic_images', None)
        if topic_images is None:
            return None
        normalizer = getUtility(IIDNormalizer)
        keyword_id = normalizer.normalize(self.keywords[0].decode('utf-8'))
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

    def getEntries(self, maximum=None, offset=0):
        """See ITopic.
        """
        weblog = self.getWeblogContentObject()
        weblog_config = IWeblogEnhancedConfiguration(weblog)
        path = '/'.join(weblog.getPhysicalPath())
        catalog = getToolByName(self, 'portal_catalog')
        ifaces = [interfaceToName(catalog.aq_parent, IWeblogEntry),
                  interfaceToName(catalog.aq_parent, IPossibleWeblogEntry)]
        results = catalog(
                object_provides={'query' : ifaces, 'operator' : 'or'},
                path={'query':path, 'level': 0},
                Subject={'query'    : self.keywords,
                         'operator' : 'and'},
                sort_on='effective',
                sort_order='reverse',
                review_state=weblog_config.published_states)
        results = results[offset:]
        if maximum is not None:
            results = results[:maximum]
        return BloggifiedCatalogResults(results)

    def __str__(self):
        """See ITopic.
        """
        return self.keywords[0]

    def __len__(self):
        """See ITopic.
        """
        return len(self.getEntries())


class AuthorTopic(Topic):
    """ Filter post by author. Joining semantic for filtering by multiple
    authors is “or”.

    XXX Deriving from Topic is awkward, as an AuthorTopic is logically
    no keyword topic.
    """

    implements(IAuthorTopic)

    def getTitle(self):
        """See ITopic.
        """
        memb_tool = getToolByName(self, 'portal_membership')
        users = []
        for user_id in self.keywords:
            info = memb_tool.getMemberInfo(user_id)
            if info is None:
                users.append(user_id)
            else:
                fullname = info['fullname'] or user_id
                users.append(fullname)               
        return ", ".join(users).decode('utf-8')

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
        weblog = self.getWeblogContentObject()
        weblog_config = IWeblogEnhancedConfiguration(weblog)
        path = '/'.join(weblog.getPhysicalPath())
        catalog = getToolByName(self, 'portal_catalog')
        ifaces = [interfaceToName(catalog.aq_parent, IWeblogEntry),
                  interfaceToName(catalog.aq_parent, IPossibleWeblogEntry)]
        results = catalog(
                object_provides={'query' : ifaces, 'operator' : 'or'},
                path={'query':path, 'level': 0},
                Creator={'query'    : self.keywords,
                         'operator' : 'or'},
                sort_on='effective',
                sort_order='reverse',
                review_state=weblog_config.published_states)
        return BloggifiedCatalogResults(results)


class TopicContainer(QuillsMixin, AcquiringActionProvider, Traversable,
                     Implicit):
    """
    >>> from zope.interface.verify import verifyClass
    >>> verifyClass(ITopicContainer, TopicContainer)
    True
    """

    implements(ITopicContainer, ITransientTopicContainer)

    __allow_access_to_unprotected_subobjects__ = EvilAATUSHack()

    def __init__(self, id, title='Topics'):
        self._id = str(id)
        self._title = title

    def getId(self):
        """
        """
        return self._id

    def Title(self):
        """
        """
        return self._title

    def getTopics(self):
        """See ITopicContainer.
        """
        keywords = self._getKeywordsForBlogEntries()
        return [Topic(kw).__of__(self) for kw in keywords]

    def getTopicById(self, id):
        """See ITopicContainer.
        """
        return Topic(id).__of__(self)

    def _getKeywordsForBlogEntries(self):
        """Return a sequence of all keywords that are associatd with
        IWeblogEntry instances contained in this IWeblog.
        """
        entries = self.getWeblog().getAllEntries()
        # Use dict rather than list to avoid duplicates
        keywords = {}
        for entry in entries:
            for kwds in entry.getTopics():
                for kw in kwds.getKeywords():
                    keywords[kw] = None
        keys = keywords.keys()
        keys.sort()
        return keys



class AuthorContainer(QuillsMixin, AcquiringActionProvider, Traversable,
                     Implicit):
    """
    >>> from zope.interface.verify import verifyClass
    >>> verifyClass(IAuthorContainer, AuthorContainer)
    True
    """

    implements(IAuthorContainer, ITransientAuthorContainer)

    __allow_access_to_unprotected_subobjects__ = EvilAATUSHack()

    def __init__(self, id, title='Authors'):
        self._id = str(id)
        self._title = title

    def getId(self):
        """
        """
        return self._id

    def Title(self):
        """
        """
        return self._title

    def getAuthors(self):
        """See IAuthorContainer.
        """
        authors = self._getAuthorsForBlogEntries()
        return [AuthorTopic(author).__of__(self) for author in authors]

    def getAuthorById(self, id):
        """See IAuthorContainer.
        """
        return AuthorTopic(id).__of__(self)

    def _getAuthorsForBlogEntries(self):
        """Return a sequence of all keywords that are associatd with
        IWeblogEntry instances contained in this IWeblog.
        """
        entries = self.getWeblog().getEntries()
        # Use dict rather than list to avoid duplicates
        authors = {}
        for entry in entries:
            for author in entry.getAuthors():
                authors[author.getId()] = None
        authors = authors.keys()
        authors.sort()
        return authors
