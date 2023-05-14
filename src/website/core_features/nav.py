from typing import Tuple

from flask import session, url_for
from flask_nav import Nav
from flask_nav.elements import Navbar, View, NavigationItem, Text, Subgroup

from website.core_features.auth import get_domain_session, get_username, is_logged_in
# from auth import get_user, get_domain_session, get_domain_session_id, is_logged_in

nav = Nav()


@nav.navigation()
def mynavbar():
    data = 'guest'
    print('data', data)
    user = get_username(session)
    login_part: Tuple[NavigationItem, ...] = tuple()
    if is_logged_in(session):
        login_part = (Text(f'Hello, {get_username(session)}'), )
    else:
        login_part = (View('Register', 'auth.register'), View('Login', 'auth.login'))
    return Navbar(
        f'Hello, {data}',
        View('Home', 'home'),
        *login_part
    )
