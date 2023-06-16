

export interface SessionAction {
    s_name: string;
}

export interface Enter extends SessionAction {
    tag: 'enter';
}

export interface Exit extends SessionAction {
    tag: 'exit';
}

export interface Register extends SessionAction {
    tag: 'register';
    username: string;
    password: string;
}

export interface Login extends SessionAction {
    tag: 'login';
    username: string;
    password: string;
}

export interface CreateStore extends SessionAction {
    tag: 'create_store';
    store_name: string;
}


export interface AddProduct extends SessionAction {
    tag: 'add_product';

}


// make sure this is updated. Don't be afraid of line-breaks; this is Typescript, it's fine.
export type Action =
    Enter | Register |
    CreateStore | AddProduct; 

export interface JsonRoot { // don't change this name.
    /**
    version of the initialization file, not of the schema.
    */
    version: string;
    init: Action[];
    "$schema": "./schema.json",
}

