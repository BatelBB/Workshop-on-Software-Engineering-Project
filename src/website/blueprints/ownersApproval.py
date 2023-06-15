from flask import Blueprint, flash, redirect, url_for, render_template

from website.core_features.domain_access.market_access import get_domain_adapter

bp = Blueprint("ownersApproval", __name__)


@bp.route('/view_approval_lists/<store_name>', methods=('POST', 'GET'))
def view_approval_lists(store_name: str):
    domain = get_domain_adapter()
    if not domain.is_logged_in:
        flash("You tried to manage approvals but you need to be logged in for that.")
        return redirect(url_for('home.home'))

    username = domain.username
    approval_lists = domain.get_approval_lists_for_store(store_name)
    owners_to_approve = approval_lists["owners"]
    bids_to_approve = approval_lists["bids"]

    return render_template("stores/view_approval_lists.html", owners_to_approve=owners_to_approve,
                           bids_to_approve=bids_to_approve, store_name=store_name, actor_username=username)


@bp.route('/approve_owner/<store_name>/<owner_name>', methods=('POST', 'GET'))
def approve_owner(store_name: str, owner_name: str):
    domain = get_domain_adapter()
    if not domain.is_logged_in:
        flash("You tried to manage approvals but you need to be logged in for that.")
        return redirect(url_for('home.home'))

    res = domain.approve_owner(store_name, owner_name)
    if res.success:
        flash("you successfuly approved")
    else:
        flash(res.description)
    return redirect(url_for('ownersApproval.view_approval_lists', store_name=store_name))


@bp.route('/approve_bid/<store_name>/<product_name>', methods=('POST', 'GET'))
def approve_bid(store_name: str, product_name: str):
    domain = get_domain_adapter()
    if not domain.is_logged_in:
        flash("You tried to manage approvals but you need to be logged in for that.")
        return redirect(url_for('home.home'))

    res = domain.approve_bid(store_name, product_name, True)
    if res.success:
        flash("you successfuly approved")
        return redirect(url_for('ownersApproval.view_approval_lists', store_name=store_name))
    else:
        flash(res.description)

@bp.route('/decline_owner/<store_name>/<owner_name>', methods=('POST', 'GET'))
def decline_owner(store_name: str, owner_name: str):
    domain = get_domain_adapter()
    if not domain.is_logged_in:
        flash("You tried to manage approvals but you need to be logged in for that.")
        return redirect(url_for('home.home'))

    res = domain.decline_owner(store_name, owner_name)
    if res.success:
        flash("you declined approved")
        return redirect(url_for('ownersApproval.view_approval_lists', store_name=store_name))
    else:
        flash(res.description)

@bp.route('/decline_bid/<store_name>/<product_name>', methods=('POST', 'GET'))
def decline_bid(store_name: str, product_name: str):
    domain = get_domain_adapter()
    if not domain.is_logged_in:
        flash("You tried to manage approvals but you need to be logged in for that.")
        return redirect(url_for('home.home'))

    res = domain.decline_bid(store_name, product_name)
    if res.success:
        flash("you declined approved")
        return redirect(url_for('ownersApproval.view_approval_lists', store_name=store_name))
    else:
        flash(res.description)