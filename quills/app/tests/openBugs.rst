Open Bugs in quills.app
=======================

This file contains tests for bugs in quills.app not yet fixed. These issues
apply to both Quills and QuillsEnabled. They might require individual fixes
in either package or in package quills.app.

On a zc.buildout enabled system you can run the tests of this file by the
command: bin/instance test -s Products.Quills -m test_docfile -t openBugs.rst

Issue #198: Images disappear blog entry is viewed by Tag Cloud or Author Name
-----------------------------------------------------------------------------

The two topic views for authors and keyword would display an empty result page
for keywords or author without associated posts. Surprisingly the archive view
behaved correctly, most certainly because it is used more intensly and hence
the bug could not go undetected there. Nonetheless we will test image handling
for all three virtual containers here.

Quills and QuillsEnabled handle image uploads differently. While a Quills blog
contains a special folder for uploads, QuillsEnabled leaves folder organization
to the user. Both however ought to be able to acquire content from containing
locations. This is where we will put our test image first.

Image loading and creation is inspired by the test-cases ATContentTypes Image
portal type and the test cases of quills.remoteblogging.

    >>> import os
    >>> import quills.app.tests as home
    >>> path = os.path.dirname(home.__file__)
    >>> file = open('%s/quills_powered.gif' % (path,), 'rb')
    >>> imageBits = file.read()
    >>> file.close()
    
    >>> id = self.portal.invokeFactory('Image', 'issue198.gif',
    ...                                title="Image for Issue 198")
    >>> image = self.portal[id]
    >>> image.setImage(imageBits)

Now we navigate to the image via the virtual URLs for archive, authors
and topics. We log in as manager, because the image is private still.

    >>> browser = self.getBrowser(logged_in=True)
    >>> browser.handleErrors = True

Before we start, let's try the canonical URL of the image.

    >>> browser.open('http://nohost/plone/%s/view' % (id,))
    >>> browser.title
    '...Image for Issue 198...'

We begin the archive. We create a post to make sure we actually have an
archive. 

    >>> self.login()
    >>> self.setRoles(('Manager',))
    >>> keyword = 'issue198kw' # id clashes would cause mayhem
    >>> entry = self.weblog.addEntry(title="Issue #198", id="issue198",
    ...                             topics=[keyword],
    ...                             excerpt="None", text="None")
    >>> entry.publish() 
    >>> year = entry.getPublicationDate().year()
    >>> month = entry.getPublicationDate().month()
    >>> browser.open('http://nohost/plone/weblog/%s/%s/%s/view'
    ...               % (year, month, id))
    >>> browser.title
    '...Image for Issue 198...'

Now the author container. The bug caused a fat internal server error here, 
which was in fact the ``TypeError: unsubscriptable object`` described
in it's issue report.

    >>> self.portal.error_log._ignored_exceptions = ()
    >>> author = entry.getAuthors()[0].getId()
    >>> browser.open('http://nohost/plone/weblog/authors/%s/%s/view'
    ...               % (author,id))
    >>> browser.title
    '...Image for Issue 198...'

And finally the keyword container.

    >>> browser.open('http://nohost/plone/weblog/topics/%s/%s/view'
    ...               % (keyword, id))
    >>> browser.title
    '...Image for Issue 198...'
