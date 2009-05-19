Open Bugs in quills.app
=======================

This file contains tests for bugs in quills.app not yet fixed. These issues
apply to both Quills and QuillsEnabled. They might require individual fixes
in either package or in package quills.app.


Issue #194: Quills breaks commenting for non-weblog content
-----------------------------------------------------------

Adding a comment to non-Quills content, say a plain Document, would raise
a NameError. This was caused by an undefined variable `redirect_target` in 
`quills.app.browser.discussionreply`.

To test for this issue we will add a comment to a Document outside the blog.

    >>> self.login()
    >>> self.setRoles(('Manager',))

    >>> id = self.portal.invokeFactory("Document", id="issue194",
    ...           title="Issue 179", description="A test case for issue #194.")
    >>> self.portal[id].allowDiscussion(allowDiscussion=True)

    >>> browser = self.getBrowser(logged_in=True)
    >>> browser.handleErrors = True
    >>> browser.open("http://nohost/plone/issue194")
    >>> browser.getControl("Add Comment").click()
    >>> browser.getControl('Subject').value = "Issue 194 fixed!"
    >>> browser.getControl('Comment').value = "This works"

See test for issue #119 why this try-except statement is here.

    >>> from urllib2 import HTTPError
    >>> try:
    ...     browser.getControl('Save').click()
    ... except HTTPError, ex:
    ...     if ex.code == 404:
    ...         browser.open("http://nohost/plone/issue194")
    ...     else:
    ...         raise
    >>> 'Issue 194 fixed!' in browser.contents
    True
    