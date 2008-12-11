Open Bugs in quills.app
=======================

This file contains tests for bugs in quills.app not yet fixed. These issues
apply to both Quills and QuillsEnabled. They might require individual fixes
in either package or in package quills.app.


Issue #115: Blog posts published in the future should not appear
----------------------------------------------------------------

Quills (ab)uses the effective date as the date of publication, but does not
hide entris until their assign effective date is reached.

Unfortunatly the code responsible for listing blog entries is duplicated quite
often in the codebase. We start with the Weblog API.

    >>> from quills.core.interfaces.weblog import IWeblog
    >>> blog = self.weblog
    >>> IWeblog.providedBy(blog)
    True

We create a entry and publish, though not yet in the future.
    

    >>> id = 'issue-115'
    >>> entry = blog.addEntry("Issue #115", "Tesing for issue 115",
    ...                       "Nothing.", id=id)
    >>> entry.publish()

This entry should have an effective date before now, or none at best. We cannot
get effective directly from the entry because it might be only an adapter.

    >>> from DateTime import DateTime # We cannot use python datetime here, alas
    >>> effective = self.portal.weblog[id].effective()
    >>> now = DateTime()
    >>> effective is None or effective <= now
    True
    
It is visible.

    >>> id in map(lambda x: x.id, blog.getEntries())
    True

Now make it become effective in the future. It should no longer be visible.

    >>> futureDate = now + 7
    >>> self.portal.weblog[id].setEffectiveDate(futureDate)
    >>> id in map(lambda x: x.id, blog.getEntries())
    False

Now same procedure through the web. Our entry should be invisible.

    >>> browser = self.getBrowser(logged_in=False)
    >>> browser.handleErrors = False
    >>> browser.open('http://nohost/plone/weblog/')
    >>> browser.getLink(url="http://nohost/plone/weblog/%s" % (id,)) is None
    True

After resetting the date it should be visible again.

    >>> self.portal.weblog[id].setEffectiveDate(effective)
    >>> browser.open('http://nohost/plone/weblog/')
    >>> browser.getLink(url="http://nohost/plone/weblog/%s" % (id,))
    <Link ...>

We do not test for draft stated entries, because those are hidden from public
viewing anyway. We have to check the archive, though.

First some preparations, like getting the archive URL prefix.

    >>> from quills.app.interfaces import IWeblogEnhancedConfiguration
    >>> weblog_config = IWeblogEnhancedConfiguration(self.portal.weblog)
    >>> archivePrefix = weblog_config.archive_format

We check through the web only. First with effective in the past.

    >>> path = "/".join([archivePrefix, "%s" % (effective.year(),)])
    >>> browser.open('http://nohost/plone/weblog/%s' % (path,))
    >>> browser.getLink(url="http://nohost/plone/weblog/%s" % (id,))
    <Link ...>

Then with effective in the future.

    >>> path = "/".join([archivePrefix, "%s" % (futureDate.year(),)])
    >>> self.portal.weblog[id].setEffectiveDate(futureDate)
    >>> browser.open('http://nohost/plone/weblog/%s' % (path,))
    >>> browser.getLink(url="http://nohost/plone/weblog/%s" % (id,)) is None
    True

Finally we should test syndication, but this would require some package implementing that
feature, which we do not want do depend on here.