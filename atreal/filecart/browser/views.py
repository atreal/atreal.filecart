from zope.interface import implements
from zope.viewlet.interfaces import IViewletManager
from zope.viewlet.interfaces import IViewlet
from zope.component import getMultiAdapter

from plone.app.kss.plonekssview import PloneKSSView
from kss.core import kssaction
from plone.app.kss.portlets import PortletReloader

from atreal.filecart.interfaces import IFileCartableView, IFileCartComments, IFileCartProvider
from atreal.filecart.portlets.cartportlet import ICartPortlet
from atreal.filecart import FileCartMessageFactory as _

class FileCartableView(PloneKSSView):
    """
    """
    implements(IFileCartableView)
    
    @kssaction
    def cleanAllComments(self):
        """
        """
        ksscore = self.getCommandSet('core')
        plonecommands = self.getCommandSet('plone')
        zopecommands = self.getCommandSet('zope')
        # Action : delete Comments
        IFileCartComments(self.context).cleanComments()
        # Portal status message
        plonecommands.issuePortalMessage(_(u"All comments deleted"), msgtype='info')
        # Refresh the viewlet Download Comments
        selector = ksscore.getHtmlIdSelector('filecart')
        zopecommands.refreshViewlet(selector, 'plone.belowcontentbody', 'atreal.filecart.viewlet.comments')
    
    @kssaction
    def showAllComments(self):
        """
        """
        ksscore = self.getCommandSet('core')
        plonecommands = self.getCommandSet('plone')
        zopecommands = self.getCommandSet('zope')
        # Action : add to request a param to show all comments in viewlet
        self.request.showAllComments = True
        # Refresh the viewlet Download Comments
        selector = ksscore.getHtmlIdSelector('filecart')
        zopecommands.refreshViewlet(selector, 'plone.belowcontentbody', 'atreal.filecart.viewlet.comments')

    @kssaction
    def addObjectToCart(self):
        ksscore = self.getCommandSet('core')
        plonecommands = self.getCommandSet('plone')
        zopecommands = self.getCommandSet('zope')
        # Action : add object to cart
        if IFileCartProvider(self.context).addToCart():
            msg = _(u"File added to cart")
        else:
            msg = _(u"File already in cart")
        # Portal status message
        plonecommands.issuePortalMessage(msg, msgtype='info')
        # Refresh the viewlet Document Actions
        selector = ksscore.getCssSelector('.documentActions')
        zopecommands.refreshViewlet(selector, 'plone.belowcontentbody', 'plone.abovecontenttitle.documentactions')
        # Refresh the portlet Cart Portlet
        portletReloader = PortletReloader(self)
        portletReloader.reloadPortletsByInterface(ICartPortlet)        
        
    @kssaction
    def delObjectFromCart(self):
        ksscore = self.getCommandSet('core')
        plonecommands = self.getCommandSet('plone')
        zopecommands = self.getCommandSet('zope')
        # Action : del object from cart
        if IFileCartProvider(self.context).delFromCart():
            msg = _(u"File deleted from cart")
        else:
            msg = _("File not in cart")
        # Portal status message
        plonecommands.issuePortalMessage(msg, msgtype='info')
        # Refresh the viewlet Document Actions
        selector = ksscore.getCssSelector('.documentActions')
        zopecommands.refreshViewlet(selector, 'plone.belowcontentbody', 'plone.abovecontenttitle.documentactions')
        # Refresh the portlet Cart Portlet
        portletReloader = PortletReloader(self)
        portletReloader.reloadPortletsByInterface(ICartPortlet)
    
