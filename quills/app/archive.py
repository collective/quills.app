#
# Authors: Maurits van Rees <m.van.rees@zestsoftware.nl>
#
# Copyright 2006, Maurits van Rees
#
# Adapted from topic.py.
#
# This file is part of Quills
#
# Quills is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# Quills is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Quills; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
###############################################################################

# Zope imports
from zope.interface import implements
from zope.component.interface import interfaceToName
from Acquisition import Implicit
from DateTime.DateTime import DateTime
from DateTime.DateTime import DateError
from OFS.Traversable import Traversable

# CMF imports
from Products.CMFCore.utils import getToolByName

# Plone imports
from Products.CMFPlone import PloneLocalesMessageFactory as _PLMF
from Products.CMFPlone.i18nl10n import monthname_msgid, monthname_english

# Quills imports
from quills.core.interfaces import IWeblogEntry
from quills.core.interfaces import IPossibleWeblogEntry
from quills.core.interfaces import IWeblogArchive
from quills.core.interfaces import IWeblogArchiveContainer
from acquiringactions import AcquiringActionProvider
from utilities import BloggifiedCatalogResults
from utilities import EvilAATUSHack
from utilities import QuillsMixin
from interfaces import ITransientArchive
from interfaces import IWeblogEnhancedConfiguration

# Check for Plone 4.0 or above
try:
    from Products.CMFPlone.factory import _IMREALLYPLONE4
except ImportError:
    PLONE40 = 0
else:
    PLONE40 = 1
    
class BaseArchive(QuillsMixin, AcquiringActionProvider, Traversable, Implicit):
    """Implementation of IWeblogArchive.
    """

    if PLONE40:
        __allow_access_to_unprotected_subobjects__ = True
    else:
        __allow_access_to_unprotected_subobjects__ = EvilAATUSHack()

    def __init__(self, *args, **kwargs):
        self._results = None

    def Description(self):
        """
        """
        return 'Archived weblog posts.'

    def __len__(self):
        """See IWeblogArchive.
        """
        return len(self.getEntries())


class ArchiveContainer(BaseArchive):
    """
    >>> from zope.interface.verify import verifyClass
    >>> verifyClass(IWeblogArchive, ArchiveContainer)
    True
    """

    implements(IWeblogArchiveContainer)

    def __init__(self, id):
        self.id = str(id)
        self._years = None
        super(ArchiveContainer, self).__init__(self, id)

    def getId(self):
        """
        """
        return self.id

    def Title(self):
        """
        """
        return self.getId()

    def _getEntryYears(self):
        """
        """
        if self._years is None:
            years= {}
            for entry in self.getEntries():
                year = entry.getPublicationDate().strftime('%Y')
                years[year] = year
            years = years.keys()
            years.sort()
            self._years = years
        return self._years

    def getSubArchives(self):
        """
        """
        years = self._getEntryYears()
        return [YearArchive(year).__of__(self) for year in years]

    def getEntries(self, maximum=None, offset=0):
        """
        """
        # Just return the weblog's getEntries.
        self._results = self.getWeblog().getEntries()[offset:]
        if maximum is not None:
            self._results = self._results[:maximum]
        return self._results


class BaseDateArchive(BaseArchive):

    implements(IWeblogArchive, ITransientArchive)

    def Title(self):
        """
        """
        return self.getId()

    def getEntries(self, maximum=None, offset=0):
        """
        """
        if self._results is None:
            min_datetime, max_datetime = self._getDateRange()
            catalog = getToolByName(self, 'portal_catalog')
            weblog = self.getWeblogContentObject()
            weblog_config = IWeblogEnhancedConfiguration(weblog)
            path = '/'.join(weblog.getPhysicalPath())
            ifaces = [interfaceToName(catalog.aq_parent, IWeblogEntry),
                      interfaceToName(catalog.aq_parent, IPossibleWeblogEntry)]
            results = catalog(
                object_provides={'query' : ifaces, 'operator' : 'or'},
                path={'query':path, 'level': 0},
                review_state=weblog_config.published_states,
                effective={
                     'query' : [min_datetime, max_datetime],
                     'range': 'minmax'}
                )
            results = results[offset:]
            if maximum is not None:
                results = results[:maximum]
            self._results = BloggifiedCatalogResults(results)
        return self._results


class YearArchive(BaseDateArchive):
    """
    >>> from zope.interface.verify import verifyClass
    >>> verifyClass(IWeblogArchive, YearArchive)
    True
    """

    def __init__(self, year):
        # Check year is of the right sort.
        int(year)
        self.year = year
        self._months = None
        super(BaseDateArchive, self).__init__(self, id)

    def getId(self):
        return str(self.year)

    def getTimeUnit(self):
        return 'Year'

    def _getEntryMonths(self):
        """
        """
        if self._months is None:
            months = {}
            for entry in self.getEntries():
                month = entry.getPublicationDate().strftime('%m')
                months[month] = month
            months = months.keys()
            months.sort()
            self._months = months
        return self._months

    def _getDateRange(self):
        min_datetime = DateTime('%s/01/01' % self.year)
        # +1 to max_datetime so that it becomes inclusive
        max_datetime = DateTime('%s/12/31' % self.year)+1
        return min_datetime, max_datetime

    def getSubArchives(self):
        """
        """
        months = self._getEntryMonths()
        return [MonthArchive(self.year, month).__of__(self) for month in months]


class MonthArchive(BaseDateArchive):
    """
    >>> from zope.interface.verify import verifyClass
    >>> verifyClass(IWeblogArchive, MonthArchive)
    True
    """

    def __init__(self, year, month):
        int(year)
        int(month)
        self.year = year
        self.month = month
        self._days = None
        super(BaseDateArchive, self).__init__(self, id)

    def getId(self):
        return str(self.month)

    def getTimeUnit(self):
        return 'Month'

    def Title(self):
        # Get utranslate script from context...
        return getToolByName(self, 'utranslate')(msgid=monthname_msgid(self.month), default=monthname_english(self.month), domain='plonelocales').capitalize()

    def _getEntryDays(self):
        """
        """
        if self._days is None:
            days = {}
            for entry in self.getEntries():
                day = entry.getPublicationDate().strftime('%d')
                days[day] = day
            days = days.keys()
            days.sort()
            self._days = days
        return self._days

    def getSubArchives(self):
        """
        """
        days = self._getEntryDays()
        return [DayArchive(self.year, self.month, day).__of__(self) for day in days]

    def _getDateRange(self):
        # XXX Test me!  Need test to ensure that months with less than 31 days
        # are correctly handled.
        min_datetime = DateTime('%s/%s/01' % (self.year, self.month))
        day = 31
        while 1:
            try:
                max_datetime = DateTime('%s/%s/%s' % (self.year, self.month, day))
                break
            except DateError:
                day = day - 1
        # +1 to max_datetime so that it becomes inclusive
        return min_datetime, max_datetime+1


class DayArchive(BaseDateArchive):
    """
    >>> from zope.interface.verify import verifyClass
    >>> verifyClass(IWeblogArchive, DayArchive)
    True
    """

    def __init__(self, year, month, day):
        int(year)
        int(month)
        int(day)
        self.year = year
        self.month = month
        self.day = day
        self._items = {}
        super(BaseDateArchive, self).__init__(self, id)

    def getId(self):
        return str(self.day)

    def getTimeUnit(self):
        return 'Day'

    def getSubArchives(self):
        """
        """
        []

    def _getDateRange(self):
        min_datetime = DateTime('%s/%s/%s' % (self.year, self.month, self.day))
        max_datetime = DateTime('%s/%s/%s' % (self.year, self.month, self.day))
        # +1 to max_datetime so that it becomes inclusive
        return min_datetime, max_datetime+1
    
    def __getitem__(self, key):
        if self._items.has_key(key):
            return self._items[key]
        min_datetime, max_datetime = self._getDateRange()
        catalog = getToolByName(self, 'portal_catalog')
        weblog = self.getWeblogContentObject()
        weblog_config = IWeblogEnhancedConfiguration(weblog)
        results = catalog(
                getId=key,
                review_state=weblog_config.published_states,
                effective={
                     'query' : [min_datetime, max_datetime],
                     'range': 'minmax'}
                )
        if len(results) != 1:
            # We can't find a suitable weblog entry, so raise a KeyError. This
            # causes the publisher to resort to looking-up/acquiring views.
            raise KeyError
        obj_brain = results[0]
        obj = obj_brain.getObject()
        self._items[key] = obj
        return obj
