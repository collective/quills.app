Open Bugs in quills.app
=======================

This file contains tests for bugs in quills.app not yet fixed. These issues
apply to both Quills and QuillsEnabled. They might require individual fixes
in either package or in package quills.app.


Issue #180: Incorrect author links in bylines
---------------------------------------------

Our screen name must differ from the login name to make this issue apparent.

    >>> self.login()
    >>> self.setRoles(('Manager',))
    >>> from Products.CMFCore.utils import getToolByName
    >>> pmtool = getToolByName(self.portal, 'portal_membership')
    >>> iAm = pmtool.getAuthenticatedMember()
    >>> myId  = iAm.getId()
    >>> oldName = iAm.getProperty('fullname')
    >>> newName = "User Issue180"
    >>> iAm.setProperties({'fullname': newName})

We need to add a page. Usually we would do so as a Contributor, but publishing
the entry without approval requires the Manager role, too.

    >>> entry = self.weblog.addEntry(title="Issue #180", id="issue180",
    ...                      excerpt="None", text="None")
    >>> entry.publish()
    
Now check the author links. First when showing the entry only.

    >>> browser = self.getBrowser()
    >>> browser.open("http://nohost/plone/weblog/issue180")
    >>> link = browser.getLink(text=newName)
    >>> link.url == "http://nohost/plone/weblog/authors/%s" % (myId,)
    True

Now the blog view.

    >>> browser.open("http://nohost/plone/weblog")
    >>> link = browser.getLink(text=newName)
    >>> link.url == "http://nohost/plone/weblog/authors/%s" % (myId,)
    True

Reset user name.
    
    >>> iAm.setProperties({'fullname': oldName})
