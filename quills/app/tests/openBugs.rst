Open Bugs in quills.app
=======================

This file contains tests for bugs in quills.app not yet fixed. These issues
apply to both Quills and QuillsEnabled. They might require individual fixes
in either package or in package quills.app.

On a zc.buildout enabled system you can run the tests of this file by the
command: bin/instance test -s Products.Quills -m test_docfile -t openBugs.rst


Issue #209 — UnicodeDecodeError in topics view
----------------------------------------------

Quills must allow non-ascii characters in topic names. This used to
work but broke with a fix for issue #195 at r87933.

We start as usual by post an entry, this time under a non-ascii
topic.

    >>> self.login()
    >>> self.setRoles(('Manager',))
    >>> keyword = 'issue198kw' # id clashes would cause mayhem
    >>> entry = self.weblog.addEntry(title="Issue #209", id="issue209",
    ...                             topics=['München'],
    ...                             excerpt="None", text="None")
    >>> entry.publish() 

Now we click that topic in the tag cloud. It should lead us to the
topic view for topic 'München'.

    >>> browser = self.getBrowser()
    >>> browser.open('http://nohost/plone/weblog')
    >>> link = browser.getLink('München')
    >>> link.click()
    >>> browser.title
    '...München...'


Issue ##203 — archive portlet broken: ValueError: invalid literal for int()
---------------------------------------------------------------------------

This bug was cause by quills.app.archive.BaseDateArchive.getId accidentally
acquiring values for the attributes 'year', 'month' or 'day'. The product
CalendarX unveiled this because it defines a page named 'day'. But in fact
any property named 'day', 'month' or 'year' that might be acquired by
climbing up the acquisition chain from an archive will cause this fault.

To test this we will simply add three pages of those names just above the
weblog. Then we will see, what the various archive report as their id.

    >>> self.login()
    >>> self.setRoles(('Manager',))
    >>> portal = self.getPortal()

We post an entry to be sure, that there is an archive.

    >>> entry = self.weblog.addEntry(title="Issue #203", id="issue203",
    ...                             excerpt="None", text="None")
    >>> entry.publish() 

No get the archives from year to day.

    >>> aYearArchive = self.weblog.getSubArchives()[0]
    >>> aMonthArchive = aYearArchive.getSubArchives()[0]
    >>> aDayArchive = aMonthArchive.getSubArchives()[0]

Create an potential acquisition target for attribute 'year' above the 
blog. Then check if ``getId`` still reports numbers...

    >>> portal.invokeFactory('Document', id='year', title='Year')
    'year'
    >>> type(int(aYearArchive.getId()))
    <type 'int'>
    >>> type(int(aMonthArchive.getId()))
    <type 'int'>
    >>> type(int(aDayArchive.getId()))
    <type 'int'>

Same for month.

    >>> portal.invokeFactory('Document', id='month', title='Month')
    'month'
    >>> type(int(aYearArchive.getId()))
    <type 'int'>
    >>> type(int(aMonthArchive.getId()))
    <type 'int'>
    >>> type(int(aDayArchive.getId()))
    <type 'int'>

Same for day.

    >>> portal.invokeFactory('Document', id='day', title='Day')
    'day'
    >>> type(int(aYearArchive.getId()))
    <type 'int'>
    >>> type(int(aMonthArchive.getId()))
    <type 'int'>
    >>> type(int(aDayArchive.getId()))
    <type 'int'>
