from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName
    
class QuillsBaseView(BrowserView):
    """ Common base class for all Quills view classes. 
    """
    def __init__(self, context, request):
        super(QuillsBaseView, self).__init__(context, request)
        self.quills_tool = getToolByName(context, 'quills_tool')

    def test(self, value, trueVal, falseVal):
        """
            helper method, mainly for setting html attributes.
        """
        if value:
            return trueVal
        else:
            return falseVal

