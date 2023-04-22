from enum import Enum


class StorePermissions(Enum):
    RetrievePurchaseHistory = 'Retrieve store purchase history'
    # InteractWithCustomer = 'Get and answer customer questions'
    Add = 'Add Product',
    Update = 'Update product quantity'
    Remove = 'Remove product'
    # ChangeDiscountPolicy = 'Change discount policy'
    # ChangePurchasePolicy = 'Change purchase policy'
    AppointManager = 'Appoint another manager'
    AppointOwner = 'Appoint another owner'
    CancelManagerAppointment = 'Cancel appointment of another manager'
    # CloseStore = 'Close store'
    RetrieveStaffDetails = 'Retrieve store staff details'


def get_store_permission_name(permission: StorePermissions) -> str:
    return StorePermissions(permission).name


def get_store_permission_description(permission: StorePermissions) -> str:
    return StorePermissions(permission).value
