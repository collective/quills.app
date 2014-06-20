# -*- coding: utf-8 -*-
from plone.i18n.normalizer.interfaces import IIDNormalizer
from zope.component import getUtility
try:
    from zope.container.interfaces import INameChooser  # Plone >= 4.1
except ImportError:
    from zope.app.container.interfaces import INameChooser


class WeblogMixin:
    """A mixin class with some helper methods for implementing
    quills.core.interfaces.IWeblog.
    """

    def _getKeywordsForBlogEntries(self):
        """Return a sequence of all keywords that are associatd with
        IWeblogEntry instances contained in this IWeblog.
        """
        entries = self.getAllEntries()
        # Use dict rather than list to avoid duplicates
        keywords = {}
        for entry in entries:
            for kw in entry.Subject:
                keywords[kw] = None
        keys = keywords.keys()
        keys.sort()
        return keys

    def _filter(self, results, maximum=None, offset=0):
        if len(results) > offset:
            if maximum is None:
                return results[offset:]
            else:
                return results[offset:offset + maximum]
        return results

    def _genUniqueId(self, folder, id, title):
        # XXX Add test-case for id generation (e.g. via addFile)
        idGen = getUtility(IIDNormalizer)
        if id:
            id = idGen.normalize(id)
        elif title:
            id = idGen.normalize(title)
        if not folder.hasObject(id):
            return id
        else:
            # Fall back to auto-gen
            return INameChooser(folder).chooseName(name='', object=None)

    def _getPortalTypeForMimeType(self, mimetype):
        # XXX Implement me properly!
        if 'image' in mimetype:
            return 'Image'
        return 'File'
