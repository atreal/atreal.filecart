from zope import schema
from zope.interface import Interface
from zope.app.container.interfaces import IContainer

from atreal.filecart import FileCartMessageFactory as _

class IFileCartLayer(Interface):
    """ Marker interface that defines a Zope 3 browser layer.
    """

class IFileCartSite(Interface):
    """ Marker interface 
    """

class ILineItem (Interface):
    """ An Item in a Cart
    """
    uid = schema.ASCIILine (title = _(u"Integer Id for a Product"))
    item_id = schema.TextLine( title = _(u"Unique Item Id"))
    name = schema.TextLine(title = _(u"Name"))
    description = schema.TextLine( title = _(u"Description"))
    size = schema.Float( title = _(u"Size"))
    def resolve ():
        """ Return the cartable object, or None if can't be found.
        """

class ILineItemFactory (Interface):
    """ Encapsulation of creating and adding a line item to a line item
        container from a cartable. sort of like an adding view
    """
    def create (cartable):
        """ Create a cartable from a line item
        """

class ILineItemContainer (IContainer):
    """ A container for line items
    """

class ILineContainerTotals (Interface):
    """ Interface for getting sizes for a collection of items
    """
    def getTotalSize ():
        """ return the total Size of all line items in the container
        """

class ICartUtility (Interface):
    def get (context, create=False, key=None):
        """ Return the user's shopping cart or none if not found. If
            create is passed then create a new one if one isn't found. If
            key is passed then return the cart corresponding to that key
            independent of the current user.
        """

    def destroy (context, key=None):
        """ Remove the current user's cart from the session if it exists.
            If key is passed then remove the cart corresponding to that
            key independent of the current user.
        """

    def getKey (context):
        """ Return a key for the shopping cart of the current user
            including anonymous users. This key can then be used to
            retrieve or destroy the cart at a later point. This is to
            support handling of notification callbacks with async
            processors.
        """

class ICart (ILineItemContainer):
    """ A Cart for files
    """
    def size ():
        """ Count the number of items in the cart
        """

class IFileCartProvider(Interface):
    """
    """

class IFileCartMarker(Interface):
    """
    """
    
class IFileCartMarkerUtility(Interface):
    """
    """

class IFileCartable(Interface):
    """
    """

class IFileCartableView(Interface):
    """
    """
    
class IFileCartComments(Interface):
    """
    """
    
class IFileCartCommentsUtility(Interface):
    """
    """
