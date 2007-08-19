

class WeblogMixin:
    """A mixin class with some helper methods for implementing
    quills.core.interfaces.IWeblog.
    """

    def _getKeywordsForBlogEntries(self):
        """Return a sequence of all keywords that are associatd with
        IWeblogEntry instances contained in this IWeblog.
        """
        # XXX Refactor me to quills.app
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
