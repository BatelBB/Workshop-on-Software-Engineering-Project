
export interface Enter extends Action {
    tag: 'enter';
    /*
    Idea: in files, sessions are given a name and then every action that uses
    this session, names which session its using. This way we can multiple sessions,
    even in the same time. Example:
    { "tag": "enter", "s_name": "yuval" },
    { "tag": "register", "s_name": "yuval", "username": "yuval", ... },
    { "tag": "enter", "s_name": "hagai" },
    { "tag": "login", "s_name": "yuval", ... },
    { "tag": "register", "s_name": "hagai", ...}
    */

    s_name: string;
}

export interface SessionAction extends Action {
    s_name: string;
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

export type Action =
    Enter | Register |
    CreateStore; // make sure this is updated. Don't be afraid of line-breaks; this is Typescript, it's fine.

export interface JsonRoot { // don't change this name.
    /**
    version of the initialization file, not of the schema.
    */
    version: string;
    init: Action[];
    "$schema": "./schema.json",
}

