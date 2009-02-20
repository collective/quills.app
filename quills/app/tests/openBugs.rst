Open Bugs in quills.app
=======================

This file contains tests for bugs in quills.app not yet fixed. These issues
apply to both Quills and QuillsEnabled. They might require individual fixes
in either package or in package quills.app.


Issues #149 & #162: Memory leak and folder listing breakage
-----------------------------------------------------------

Both issues are cause by the way Quills wraps up Catalog Brains into an
IWeblogEntry adapter. It sets this wrapper class with "useBrains" of
Products.ZCatalog.Catalog. Doing so on each query causes the memory leak, as
the Catalog creates a class on the fly around the class passed to useBrains.
Never resetting the class causes the folder listing to break, because now
all catalog queries, even those from non Quills code, use Quills custom Brain.
This brain however defines methods which are simple member variable in the
default Brain, causing those clients to break.

To test for those bug, first publish a post, then render the Weblog View once.
This will cause some of the incriminating code to be called. Testing all 
occurances would not be sensible. A fix must make sure to break all those
calls by renaming the custom catalog class!

An exception is raised that, because the specified portal type does not exist.
In fact the type specified is "None". This is happens because no default
type is configured for Products.Quills weblogs.
Create a fresh blog, in the case someone might accidentally have set a default
portal type before. Populate it a little.

    >>> entry = self.weblog.addEntry('Tesing issue # 149 & #162', 'Nothing',
    ...                       'Nothing', id="issue-158")
    >>> entry.publish()
    >>> browser = self.getBrowser(logged_in=True)
    >>> browser.handleErrors = True
    >>> browser.open('http://nohost/plone/weblog/')

Now query a non Quills object from the catalog (in fact no query should ever
return a custom Quills brain). At least the Welcome message should exist.
Then check if the brain is a Quills adapter.

    >>> from Products.CMFCore.utils import getToolByName
    >>> catalog = getToolByName(self.portal, 'portal_catalog')
    >>> results = catalog(path="/", portal_type="Document")
    >>> len(results) > 0
    True

    >>> from quills.core.interfaces import IWeblogEntry
    >>> IWeblogEntry.providedBy(results[0])
    False
