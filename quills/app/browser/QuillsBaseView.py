from Products.Five import BrowserView
    
class QuillsBaseView(BrowserView):
    """ Common base class for all Quills view classes. 
    """
    def test(self, value, trueVal, falseVal):
        """
            helper method, mainly for setting html attributes.
        """
        if value:
            return trueVal
        else:
            return falseVal

