from flask import Blueprint, request, render_template, flash, redirect, url_for

from src.domain.main.StoreModule.Product import Product
from website.core_features.domain_access.market_access import get_domain_adapter

bp = Blueprint("searching", __name__)


@bp.route('/search_product', methods=['GET'])
def search_product():
    domain = get_domain_adapter()
    query = request.args.get('query', '')
    price_range = request.args.get('price_range', '')
    product_ranking = request.args.get('product_ranking', '')
    category = request.args.get('category', '')

    ProductsOfStore = domain.get_all_products()

    products_with_store = []
    categories = set()
    for store_name, products in ProductsOfStore.items():
        for product in products:
            categories.add(product.category)
            if query.lower() in product.name.lower() or query.lower() in product.category.lower() or query.lower() in product.keywords_str.lower().split('#'):
                if price_range:
                    low, high = map(int, price_range.split('-'))
                    if not (low <= product.price <= high):
                        continue
                if product_ranking:
                    low, high = map(int, product_ranking.split('-'))
                    if not (low <= product.rate <= high):
                        continue
                if category:
                    if product.category != category:
                        continue
                products_with_store.append((store_name, product))

    return render_template('buying/search_product.html', products=products_with_store, categories=categories)


