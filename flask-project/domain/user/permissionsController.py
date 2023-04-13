# TODO: make it threadsafe?
# TODO: manager permissions


class permissionsController:
    __instance = None  # __ is like private
    ownerships: dict
    managers: dict
    appointment: dict

    @staticmethod
    def get_instance():
        if permissionsController.__instance is None:
            permissionsController()

        return permissionsController.__instance

    def __init__(self):
        self.ownerships = {}
        self.managers = {}
        self.appointment = {}
        self.__instance = self

    def createShop(self, shopID: int, founderID):
        self.ownerships[shopID] = [founderID]
        self.managers[shopID] = []
        self.appointment[founderID] = []

    def isOwner(self, userID: int, shopID: int):
        if userID in self.ownerships.get(shopID):
            return True
        return False

    def isManager(self, userID: int, shopID: int):
        if userID in self.managers.get(shopID):
            return True
        return False

    def isAppointedByMe(self, heID, meID):
        return heID in self.appointment[meID]

    def appointOwner(self, appointerID: int, appointedID: int, shopID: int):
        if self.isOwner(appointerID, shopID):
            self.ownerships[shopID].append(appointedID)
            self.appointment[appointerID].append(appointedID)
            self.appointment[appointedID] = []
        else:
            raise Exception(f"userid: {appointerID} is not an owner of shop: {shopID}\n")

    def appointManager(self, appointerID: int, appointedID: int, shopID: int):
        if self.isOwner(appointerID, shopID):
            self.managers[shopID].append(appointedID)
            self.appointment[appointerID].append(appointedID)
        else:
            raise Exception(f"userid: {appointerID} is not an owner of shop: {shopID}\n")

    def fireManager(self, empID: int, managerID: int, shopID: int):
        if not self.isOwner(empID, shopID):
            raise Exception(f"user {empID} is not owner of {shopID}")
        if not self.isManager(managerID, shopID):
            raise Exception(f"user {managerID} is not manager of {shopID}")
        if not self.isAppointedByMe(managerID, empID):
            raise Exception(f"user {managerID} is not appointed by {empID}")
        else:
            self.managers[shopID].remove(managerID)

    def fireOwner(self, empID: int, ownerToGoID: int, shopID: int):
        if not self.isOwner(empID, shopID):
            raise Exception(f"user {empID} is not owner of {shopID}")
        if not self.isOwner(ownerToGoID, shopID):
            raise Exception(f"user {ownerToGoID} is not manager of {shopID}")
        if not self.isAppointedByMe(ownerToGoID, empID):
            raise Exception(f"user {ownerToGoID} is not appointed by {empID}")
        else:
            for ownerID in self.appointment[ownerToGoID]:
                self.fireOwner(ownerToGoID, ownerID, shopID)

            self.ownerships[shopID].remove(ownerToGoID)
            self.appointment[empID].remove(ownerToGoID)
            self.appointment.pop(ownerToGoID)

    def checkManagerPermission(self, permission: int, shopID: int, ManagerID: int):
        ...

