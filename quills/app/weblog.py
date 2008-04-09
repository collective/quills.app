

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
                return results[offset:offset+maximum]
        return results

    def _genUniqueId(self, folder, id, title):
        if id:
            if not folder.hasObject(id):
                return id
        if id is None and title:
            id = getUtility(IIDNormalizer).normalize(title)
            if not folder.hasObject(id):
                return id
        else:
            # No id or title, so just generate something random (and unique)
            id = INameChooser(folder).chooseName(name='', object=None)
        return id

    def _getPortalTypeForMimeType(self, mimetype):
        # XXX Implement me properly!
        if 'image' in mimetype:
            return 'Image'
        return 'File'


