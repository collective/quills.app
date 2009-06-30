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
