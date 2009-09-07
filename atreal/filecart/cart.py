from persistent import Persistent

from BTrees.OOBTree import OOBTree
from AccessControl import getSecurityManager

from zope.component import getMultiAdapter, queryUtility, getUtility
from zope.interface import implements
from zope.app.container.ordered import OrderedContainer

from Products.CMFCore.utils import getToolByName


from atreal.filecart.content import LineItemFactory
from atreal.filecart.interfaces import IFileCartProvider, ICart, ICartUtility


class FileCartProvider(object):
    """
    """
    implements(IFileCartProvider)
    
    _cart = None
    
    def __init__(self, context):
        """
        """
        self.context = context
    
    @property
    def cart(self):
        if self._cart is not None:
            return self._cart
        cart_manager = queryUtility(ICartUtility)
        self._cart = cart_manager.get(self.context, create=True)
        return self._cart
    
    def addToCart(self):
        """
        """
        if self.isInCart():
            return False
        item_factory = LineItemFactory(self.cart, self.context)
        item_factory.create()
        return True

    def delFromCart(self):
        """
        """
        if not self.isInCart():
            return False
        self.cart.__delitem__(self.context.UID())
        return True

    def isInCart(self):
        """
        """
        if self.context.UID() in self.cart:
            return True
        return False


class Cart (OrderedContainer):
    """ A file cart
    """
    implements (ICart)

    last_item = None
    
    def size (self):
        return len (self.keys ())

    def __setitem__ (self, key, value):
        super (Cart, self).__setitem__ (key, value)
        self.last_item = key
        
    def __delitem__ (self, key):
        if not key in self:
            return
        super (Cart, self).__delitem__ (key)
        if self.last_item == key:
            if len (self) > 0:
                self.last_item = self.keys ()[-1]
            else:
                self.last_item = None


class CartUtility (Persistent):
    """
    """
    implements (ICartUtility)

    def __init__(self):
        self._sessions = OOBTree()

    def get(self, context, create=False, key=None):
        """ Get the persistent cart. It does not persist for anonymous users or
        one time only usage (things like one page buy and checkout)
        """
        if key is not None:
            if create:
                raise ValueError('Invalid combination of optional '
                                 'parameters "create" and "key".')
            name, value = self._decodeKey(key)
            if name == 'user':
                return self._getCartForUser(context, value)
            elif name == 'session':
                return self._getCartForSession(context, browser_id=value)
            elif name == 'oneshot':
                return self._getDisposableCart(context, browser_id=value)
        else:
            uid = getSecurityManager().getUser().getId()
            if uid is not None:
                # Check if there is a session cart - if there is we need to transfer it
                session_cart = self._getCartForSession(context, False)
                if session_cart:
                    session_cart.member_id = uid
                    self._sessions[uid] = session_cart
                    self._destroyCartForSession(context)
                return self._getCartForUser(context, uid, create)
            else:
                return self._getCartForSession(context, create)


    def _getCartForUser(self, context, uid, create=False):
        cart = self._sessions.get(uid)
        if cart or not create:
            return cart
        cart = Cart()
        cart.member_id = uid
        self._sessions[uid] = cart
        return cart


    def _getCartForSession(self, context, create=False, browser_id=None):
        session_manager = getToolByName(context, 'session_data_manager')
        if browser_id is None:
            if not session_manager.hasSessionData() and not create:
                return
            session = session_manager.getSessionData()
        else:
            session = session_manager.getSessionDataByKey(browser_id)
            if session is None:
                return
        if not session.has_key('getpaid.cart'):
            if create:
                session['getpaid.cart'] = cart = Cart()
            else:
                return None
        return session['getpaid.cart']

    def _getDisposableCart(self, context, browser_id=None):
        return Cart()
        


    def destroy(self, context, key=None):
        """ Destroy the cart.
        """
        if key is not None:
            name, value = self._decodeKey(key)
            if name == 'user':
                return self._destroyCartForUser(context, value)
            elif name == 'session':
                return self._destroyCartForSession(context, value)
        else:
            uid = getSecurityManager().getUser().getId()
            if uid is not None:
                return self._destroyCartForUser(context, uid)
            else:
                return self._destroyCartForSession(context)


    def _destroyCartForUser(self, context, uid):
        if self._sessions.has_key(uid):
            del self._sessions[uid]


    def _destroyCartForSession(self, context, browser_id=None):
        session_manager = getToolByName(context, 'session_data_manager')
        if browser_id is None:
            if not session_manager.hasSessionData(): #nothing to destroy
                return None
            session = session_manager.getSessionData()
        else:
            session = session_manager.getSessionDataByKey(browser_id)
            if session is None:
                return
        if not session.has_key('getpaid.cart'):
            return
        del session['getpaid.cart']


    def getKey(self, context):
        """Return key that can be used to recover the cart for the
        current user or session.
        """
        uid = getSecurityManager().getUser().getId()
        if uid is not None:
            return 'user:%s' % uid
        else:
            session_manager = getToolByName(context, 'session_data_manager')
            if not session_manager.hasSessionData():
                return None
            session = session_manager.getSessionData()
            if not session.has_key('getpaid.cart'):
                return None
            return 'session:%s' % session.token


    def _decodeKey(self, key):
        try:
            name, value = key.split(':', 1)
        except ValueError:
            raise ValueError('Malformed key: %s' % key)
        if name not in ['user', 'session', 'oneshot']:
            raise ValueError('Malformed key: %s' % key)
        return name, value


    def manage_fixupOwnershipAfterAdd(self):
        pass

