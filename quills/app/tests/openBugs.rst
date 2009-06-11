Open Bugs in quills.app
=======================

This file contains tests for bugs in quills.app not yet fixed. These issues
apply to both Quills and QuillsEnabled. They might require individual fixes
in either package or in package quills.app.


Issue #195: Topic view shows only one keyword
---------------------------------------------

This obviously only hurts when one tries to filter by more than just
one keyword. Filtering by multiple keywords is done appending more
keywords to the blog URL, separated by slashes.

First blog a post in more than one catagory.

    >>> self.login()
    >>> self.setRoles(('Manager',))

    >>> entry = self.weblog.addEntry(title="Issue #195", id="issue195",
    ...                      topics=['i195TopicA', 'i195TopicB'],
    ...                      excerpt="None", text="None")
    >>> entry.publish()

Now browse the weblog by those two keywords. They should appear in a
heading.

    >>> browser = self.getBrowser()
    >>> browser.handleErrors = True
    >>> browser.open("http://nohost/plone/weblog/topics/i195TopicA/i195TopicB")

    >>> import re
    >>> r1 = 'i195TopicA.+i195TopicB|i195TopicB.+i195TopicA'
    >>> r2 = '<h1>(%s)</h1>' % (r1,)
    >>> re.search(r2, browser.contents)
    <_sre.SRE_Match object at ...>

    >>> re.search(r1, browser.title)
    <_sre.SRE_Match object at ...>

Author topics face the same problem. So, the same with them. We need a second
author first.

    >>> from Products.CMFCore.utils import getToolByName
    >>> aclUsers = getToolByName(self.getPortal(), 'acl_users')
    >>> aclUsers.userFolderAddUser('Issue195Author2', 'issue195',['manager'],[])
    >>> rawPost = self.portal.weblog['issue195']
    >>> rawPost.setCreators(rawPost.Creators()+('Issue195Author2',))

    >>> authors = rawPost.Creators()
    >>> browser.open("http://nohost/plone/weblog/authors/%s/%s" % authors)

    >>> import re
    >>> from string import Template
    >>> templ = Template('${a}.+${b}|${b}.+${a}')
    >>> r1 = templ.substitute(a=authors[0], b=authors[1])
    >>> r2 = '<h1>(%s)</h1>' % (r1,)  
    >>> re.search(r2, browser.contents)
    <_sre.SRE_Match object at ...>

    >>> re.search(r1, browser.title)
    <_sre.SRE_Match object at ...>



   
