from flask import Blueprint, flash, redirect, url_for, render_template

from website.core_features.domain_access.market_access import get_domain_adapter

bp = Blueprint("ownersApproval", __name__)


@bp.route('/view_approval_lists/<store_name>', methods=('POST', 'GET'))
def view_approval_lists(store_name: str):
    domain = get_domain_adapter()
    if not domain.is_logged_in:
        flash("You tried to manage approvals but you need to be logged in for that.")
        return redirect(url_for('home.home'))

    approvals_lists = domain.get_approval_lists_for_store(store_name)
    if approvals_lists["owners"] != {}:
        approvals_lists["owners"] = approvals_lists["owners"].dictionary
    return render_template("stores/view_approval_lists.html", owners_to_approve=approvals_lists["owners"],
                           bids_to_approve=approvals_lists["bids"], store_name=store_name)


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