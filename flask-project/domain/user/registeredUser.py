import string

from domain.interfaces import IRegisteredUser
import permissionsController


class RegisteredUser(IRegisteredUser):
    pc: permissionsController
    ownedStores: list
    managedStores: list
    id: int

    def __init__(self, username: string, password: string, id: int):
        self.ownedStores = []
        self.ownedStores = []
        super().username = username
        super().password = password
        self.id = id
        permissionsController     #initialize pc

    def create_store(self, shopID: int):
        self.ownedStores.append(shopID)
        self.pc.createShop(shopID)

    def appoint_owner(self, shop, empID):
        self.pc.appointOwner(id, empID, shop)

    def appoint_manager(self, shop, empID):
        self.pc.appointManager(id, empID, shop)

    def fire_manager(self, shop, empID):
        self.pc.fireManager(id, empID, shop)

    def fire_owner(self, shop, empID):
        self.pc.fireManager(id, empID, shop)

    # for owners only
    def close_store(self):
        ...

    def get_shop_personnel(self, shop_id):
        ...
