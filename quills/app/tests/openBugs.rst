Open Bugs in quills.app
=======================

This file contains tests for bugs in quills.app not yet fixed. These issues
apply to both Quills and QuillsEnabled. They might require individual fixes
in either package or in package quills.app.

Issue #158 — "Add Entry" of the Weblog Admin portlet fails
-----------------------------------------------------------

An exception is raised that, that the specified portal type does not exist.
In fact the type specified is "None". This is happens because no default
type is configured for a Products.Quills weblog.

Create a fresh blog, in the case someone might accidentally have set a default
portal type before. Populate it a little.

    >>> self.setRoles(("Manager",))
    >>> blog = self.createBlog('issue-158')
    >>> blogFolder = self.portal['issue-158']
    >>> entry = blog.addEntry('Tesing issue #158', 'Nothing', 'Nothing', id="issue-158")
    >>> entry.publish()

Now click the "Add Entry" link.

    >>> browser = self.getBrowser(logged_in=True)
    >>> browser.handleErrors = True
    >>> browser.open('http://nohost/plone/issue-158/')
    >>> browser.getLink(text='Add Entry').click()
    >>> "Add Weblog Entry" in browser.contents
    True

