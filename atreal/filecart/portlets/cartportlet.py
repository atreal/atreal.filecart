from zope.interface import Interface
from zope.interface import implements
from zope.interface.interfaces import IInterface
from zope.component import queryUtility

from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base

from zope import schema
from zope.formlib import form
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from atreal.filecart.browser.filecart import CartProvider
from atreal.filecart import FileCartMessageFactory as _

class ICartPortlet(IPortletDataProvider):
    """A portlet

    It inherits from IPortletDataProvider because for this portlet, the
    data that is being rendered and the portlet assignment itself are the
    same.
    """

class Assignment(base.Assignment):
    """Portlet assignment.

    This is what is actually managed through the portlets UI and associated
    with columns.
    """

    implements(ICartPortlet)

    def __init__(self):
        pass

    @property
    def title(self):
        """This property is used to give the title of the portlet in the
        "manage portlets" screen.
        """
        return "Cart Portlet"

class Renderer(base.Renderer, CartProvider):
    """Portlet renderer.

    This is registered in configure.zcml. The referenced page template is
    rendered, and the implicit variable 'view' will refer to an instance
    of this class. Other methods can be added and referenced in the template.
    """

    render = ViewPageTemplateFile('cartportlet.pt')
    
    lastitembrain = None
    lastitemthumb = None
    
    @property
    def available(self):
        # Use portal_membership tool for checking permissions
        mtool = self.context.portal_membership
        checkPermission = mtool.checkPermission
        # checkPermissions returns true if permission is granted
        if checkPermission('atreal.filecart: Use Cart', self.context):
            return True
        return False

    
    def isOverrideAlbumViewInstalled(self):
        """ 
        """
        if queryUtility(IInterface, name=u'atreal.override.albumview.IOverrideAlbumViewSite', default=False):
            return True
        return False
    
    def isRichFileImageInstalled(self):
        """ 
        """
        if queryUtility(IInterface, name=u'atreal.richfile.image.IRichFileImageSite', default=False):
            return True
        return False  
    
    def getLastElement (self):
        if self.cart.last_item is None :
            return False
        
        if self.isRichFileImageInstalled() == False:
            richfile_image = False
        else:
            richfile_image = self.context.portal_catalog(object_provides='atreal.richfile.image.interfaces.IImage',UID=self.cart.last_item)
            if len(richfile_image) != 1:
                richfile_image = False
            else:
                richfile_image = True
        
        pc = self.context.portal_catalog(UID=self.cart.last_item)
        if len(pc)!=1:
            return
        brain = pc[0]
        thumb = None
        if brain.portal_type == "Image":
            thumb = brain.getURL()+'/image_thumb'
        elif richfile_image == True:
            thumb = brain.getURL()+'/rfimage/thumb'
        elif self.isOverrideAlbumViewInstalled():
            thumb = self.context.portal_url()+'/rf_'+brain.getIcon
        self.lastitembrain = brain
        self.lastitemthumb = thumb
        return True


# NOTE: If this portlet does not have any configurable parameters, you can
# inherit from NullAddForm and remove the form_fields variable.

class AddForm(base.NullAddForm):
    form_fields = form.Fields(ICartPortlet)
    label = _(u"Add Cart Portlet")
    description = _(u"This portlet displays The number of item in your cart and the last item added.")
    
    def create(self):
        return Assignment()

