type str = string;
type bool = boolean;
type float = number;
type int = number;
/**     def register(self, username: str, password: str) -> Response[bool]: */
export interface Action_register {
    tag: "register";
    username: string;
    password: string;
}


/**     def register_admin(self, username: str, password: str, is_admin: bool = True) -> Response[bool]: */
export interface Action_register_admin {
    tag: "register_admin";
    username: string;
    password: string;
    is_admin: boolean;
}


/**     def login(self, username: str, encrypted_password: str) -> Response[bool] */
export interface Action_login {
    tag: "login";
    username: string;
    /**
     * should NOT be encrypted, ignore the name
     */
    encrypted_password: string;
}


/**     def logout(self) -> Response[bool] */
export interface Action_logout {
    tag: "logout";
}


/**     def open_store(self, store_name: str) -> Response[bool]: */
export interface Action_open_store {
    tag: "open_store";
    store_name: string;
}


/**     def add_to_cart(self, store_name: str, product_name: str, quantity: int = 1) -> Response[bool] */
export interface Action_add_to_cart {
    tag: "add_to_cart";
    store_name: string;
    product_name: string;
    quantity: number;
}


/**     def purchase_shopping_cart(self, payment_method: str, payment_details: list, address: str, postal_code: str, city: str, country: str) */
export interface Action_purchase_shopping_cart {
    tag: "purchase_shopping_cart";
    payment_method: str;
    payment_details: [string, string, string];
    address: str; postal_code: str; city: str; country: str;
}


/**     def close_store(self, store_name: str) -> Response[bool] */
export interface Action_close_store {
    tag: "close_store"; store_name: str;
}


/**     def appoint_manager(self, appointee: str, store: str, ) -> Response[bool] */
export interface Action_appoint_manager {
    tag: "appoint_manager"; appointee: str; store: str;
}


/**     def appoint_owner(self, appointee: str, store: str) -> Response[bool] */
export interface Action_appoint_owner {
    tag: "appoint_owner"; appointee: str, store: str;
}


/**     def approve_owner(self, appointee: str, store: str, is_approve: bool) */
export interface Action_approve_owner {
    tag: "approve_owner"; appointee: str, store: str, is_approve: bool;
}

/** def add_product(self, store_name: str, product_name: str, category: str, price: float, quantity: int,
                    keywords: list[str] = None) -> Response[bool]:*/
export interface Action_add_product {
tag: "add_product",
store_name: str, product_name: str, category: str, price: float, quantity: int,
                    keywords: str[];
}

type Permission = "RetrievePurchaseHistory" |
    "RetrieveStaffDetails" |
    "InteractWithCustomer" |
    "Add" |
    "AddRule" |
    "Update" |
    "Remove" |
    "ChangeDiscountPolicy" |
    "ChangePurchasePolicy" |
    "AppointManager" |
    "AppointOwner" |
    "OpenAuction" |
    "OpenLottery" |
    "StartBid" |
    "ApproveBid";
/**     def add_permission(self, store: str, appointee: str, permission: Permission | str) -> Response[bool]: */
export interface Action_add_permission {
    tag: "add_permission";
    store: str, appointee: str, permission: Permission;
}


/**     def purchase_with_non_immediate_policy(self, store_name: str, product_name: str,                                           payment_method: str, payment_details: list[str], address: str,postal_code: str, how_much: float, city: str, country: str) */
export interface Action_purchase_with_non_immediate_policy {
    tag: "purchase_with_non_immediate_policy"; store_name: str, product_name: str, payment_method: str, payment_details: [str, str, str], address: str, postal_code: str, how_much: number, city: str, country: str
}


/**     def start_auction(self, store_name: str, product_name: str, initial_price: float, duration: int) -> Response[bool] */
export interface Action_start_auction {
    tag: "start_auction"; store_name: str, product_name: str, initial_price: float, duration: int
}


/**     def start_lottery(self, store_name: str, product_name: str) -> Response: */
export interface Action_start_lottery {
    tag: "start_lottery"; store_name: str, product_name: str;
}


/**     def start_bid(self, store_name: str, product_name: str) -> Response: */
export interface Action_start_bid {
    tag: "start_bid"; store_name: str, product_name: str;
}


/**     def approve_bid(self, store_name: str, product_name: str, is_approve: bool) -> Response: */
export interface Action_approve_bid {
    tag: "approve_bid"; store_name: str, product_name: str, is_approve: bool
}


/**     def add_purchase_simple_rule(self, store_name: str, product_name: str, gle: str, amount: int) -> Response: */
export interface Action_add_purchase_simple_rule {
    tag: "add_purchase_simple_rule"; store_name: str, product_name: str, gle: str, amount: int
}


/**     def add_purchase_complex_rule(self, store_name: str, p1_name: str, gle1: str, amount1: int, p2_name: str, gle2: str,        amount2: int, complex_rule_type: str) -> Response: */
export interface Action_add_purchase_complex_rule {
    tag: "add_purchase_complex_rule"; store_name: str, p1_name: str, gle1: str, amount1: int, p2_name: str, gle2: str, amount2: int, complex_rule_type: str
}


/**     def add_basket_purchase_rule(self, store_name: str, min_price: float) -> Response: */
export interface Action_add_basket_purchase_rule {
    tag: "add_basket_purchase_rule"; store_name: str, min_price: float;
}


/**     def send_message(self, recipient, content):   */
export interface Action_send_message {
    tag: "send_message";
    recipient: string;
    content: string;
}



// make sure this is updated. Don't be afraid of line-breaks; this is Typescript, it's fine.
export type Action = Action_register | Action_register_admin | Action_login | Action_logout |
Action_open_store | Action_add_to_cart | Action_purchase_shopping_cart | Action_close_store |
Action_appoint_manager | Action_appoint_owner | Action_approve_owner | Action_add_permission |
 Action_purchase_with_non_immediate_policy | Action_start_auction | Action_start_lottery | Action_start_bid |
 Action_approve_bid | Action_add_purchase_simple_rule | Action_add_purchase_complex_rule |
  Action_add_basket_purchase_rule | Action_send_message | Action_add_basket_purchase_rule
  | Action_add_product
    ;

export interface JsonRoot {
    // don't change this name.
    /**
      version of the initialization file, not of the schema.
      */

    version: string;
    init: Action[];
    $schema: "./schema.json";
}


