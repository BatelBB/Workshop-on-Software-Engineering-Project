from enum import Enum


class Permission(Enum):
    RetrievePurchaseHistory = 'Retrieve store purchase history'
    RetrieveStaffDetails = 'Retrieve store staff details'
    InteractWithCustomer = 'Get and answer customer questions'
    Add = 'Add a Product'
    AddRule = 'Add a Store-Role'
    Update = 'Update product details'
    Remove = 'Remove product'
    ChangeDiscountPolicy = 'Change discount policy'
    ChangePurchasePolicy = 'Change purchase policy'
    AppointManager = 'Appoint another manager'
    AppointOwner = 'Appoint another owner'
    CancelManagerAppointment = 'Cancel appointment of another manager'
    CancelOwnerAppointment = 'Cancel appointment of another owner'
    CloseStore = 'Close store'
    ReopenStore = 'Reopen store'
    OpenAuction = 'Open Auction'
    OpenLottery= 'Open Lottery'
    StartBid = 'Start a bid'
    ApproveBid = 'Approve a bid'



def get_permission_name(permission: Permission) -> str:
    return Permission(permission).name


def get_permission_description(permission: Permission) -> str:
    return f'\'{Permission(permission).value}\''


def get_default_owner_permissions() -> set[Permission]:
    return {p for p in Permission}


def get_default_manager_permissions() -> set[Permission]:
    return {Permission.RetrievePurchaseHistory, Permission.InteractWithCustomer}
