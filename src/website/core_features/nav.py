from typing import Tuple

from flask import session, url_for
from flask_nav import Nav
from flask_nav.elements import Navbar, View, NavigationItem, Text, Subgroup

# from auth import get_user, get_domain_session, get_domain_session_id, is_logged_in
from website.core_features.domain_access.market_access import get_domain_adapter

nav = Nav()


@nav.navigation()
def mynavbar():
    domain = get_domain_adapter()
    login_part: Tuple[NavigationItem, ...] = tuple()
    if domain.is_logged_in:
        login_part = (Text(f'Hello, {domain.username}'), View('Logout', 'auth.logout'))
    else:
        login_part = (View('Register', 'auth.register'), View('Login', 'auth.login'))
    return Navbar(
        f'Logo here',
        View('Home', 'home.home'),
        *login_part
    )
