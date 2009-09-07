from persistent import Persistent

from zope import component
from zope.interface import implements
from zope.app.intid.interfaces import IIntIds
from zope.app.container.interfaces import ILocation
from zope.annotation.interfaces import IAttributeAnnotatable

from atreal.filecart.interfaces import ILineItem, IFileCartable


class LineItem( Persistent ):
    """
    an item in the cart

    lineitems are not generically attribute annotatable, which typically requires
    zodb persistence, instead to enable storage in other mediums, we use a specific
    limited set of components that use annotations on line items, specifically the
    workflow engine to enable fulfillment workflows on individual items.
    """
    implements( ILineItem, IAttributeAnnotatable )

    # default attribute values, item_id is required and has no default
    name = ""
    description = ""
    quantity = 0
    uid = None
    

    def clone( self ):
        clone = self.__class__.__new__( self.__class__ )
        clone.__setstate__( self.__getstate__() )
        if ILocation.providedBy( clone ):
            del clone.__name__, clone.__parent__
        return clone

    def resolve( self ):
        utility = component.getUtility( IIntIds )
        return utility.queryObject( self.uid )



class LineItemFactory( object ):
    """
    adapts to cart and content (payable marker marked), and creates a line item
    from said item for cart.
    """
    
    def __init__ (self, cart, content):
        self.cart = cart
        self.content = content

    def create (self):
        if self.checkExistsInCart (self.content):
            return
        
        cartable = self.checkCartable (self.content)
        nitem = self.createLineItem (cartable)
        self.cart[ nitem.item_id ] = nitem
        return nitem
        
    def checkExistsInCart (self, content):
        item_id = content.UID ()
        if item_id in self.cart:
            return True
    
    def checkCartable (self, content):
        return IFileCartable.providedBy(content)
    
    def createLineItem (self, cartable):
        nitem = LineItem()
        nitem.item_id = self.content.UID() # archetypes uid
        
        # we use intids to reference content that we can dereference cleanly
        # without access to context.
        nitem.uid = component.getUtility( IIntIds ).register( self.content )
        
        def getUnicodeString( s ):
            """Try to convert a string to unicode from utf-8, as this is what Archetypes uses"""
            if type( s ) is type( u'' ):
                # this is already a unicode string, no need to convert it
                return s
            elif type( s ) is type( '' ):
                # this is a string, let's try to convert it to unicode
                try:
                    return s.decode( 'utf-8' )
                except UnicodeDecodeError, e:
                    # not utf-8... return as is and hope for the best
                    return s

        # copy over information regarding the item
        nitem.name = getUnicodeString( self.content.Title() )
        nitem.description = getUnicodeString( self.content.Description() )
        return nitem

