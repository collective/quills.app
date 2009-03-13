Open Bugs in quills.app
=======================

This file contains tests for bugs in quills.app not yet fixed. These issues
apply to both Quills and QuillsEnabled. They might require individual fixes
in either package or in package quills.app.

Issue #172 — Can't log comments from default view on weblog entries
-------------------------------------------------------------------

Quills default view for Weblog Entries is named 'weblogentry_view'. Plone
however links to individual items via the 'view' alias. This happens for
instance in collections or the recent items portlet. The Weblog Entries
still get rendered, important actions are missing though, e.g. the user
actions for copy/paste/delete or workflow actions. The commenting button 
is also missing.

We will need write access to the blog.

    >>> self.logout()
    >>> self.login()
    >>> self.setRoles(("Manager",))

Create a discussable weblog entry first.

    >>> from quills.app.browser.weblogview import WeblogEntryView
    >>> traverseTo = self.portal.restrictedTraverse # for brevity
    >>> entry = self.weblog.addEntry("Test for issue #172", "Nothing",
    ...                              "Nothing", id="issue-172")
    >>> entry_content = entry.getWeblogEntryContentObject()
    >>> entry_content.allowDiscussion(allowDiscussion=True)
    >>> entry.publish()

There should be a fully functionaly WeblogEntryView at 'weblogentry_view'.

    >>> browser = self.getBrowser(logged_in=True)
    >>> browser.handleErrors = False
    >>> browser.open('http://nohost/plone/weblog/issue-172/weblogentry_view')

That inculdes actions like cut and paste,

    >>> browser.getLink(text='Actions') # of issue-172/weblogentry_view
    <Link ...>

and also workflow control,

    >>> browser.getLink(text='State:') # of issue-172/weblogentry_view
    <Link ...>

    >>> browser.getForm(name='reply') # of issue-172/weblogentry_view
    <zope.testbrowser.browser.Form object at ...>

and finally commenting, which must be enabled, of course.

The same should be available when we navigate to issue-172/view.

    >>> browser = self.getBrowser(logged_in=True)
    >>> browser.handleErrors = False
    >>> browser.open('http://nohost/plone/weblog/issue-172/view')

That inculdes actions like cut and paste,

    >>> browser.getLink(text='Actions') # of issue-172/view
    <Link ...>

and also workflow control,

    >>> browser.getLink(text='State:') # of issue-172/view
    <Link ...>

and finally commenting, which must be enabled, of course.

    >>> browser.getForm(name='reply') # of issue-172/view
    <zope.testbrowser.browser.Form object at ...>
