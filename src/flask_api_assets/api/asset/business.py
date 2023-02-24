"""Business logic for /asset API endpoints."""
from http import HTTPStatus

from flask import jsonify, url_for
from flask_restx import abort, marshal

from flask_api_assets import db
from flask_api_assets.api.asset.dto import pagination_model, asset_name
from flask_api_assets.models.asset import Asset


def create_asset(asset_dict):
    name = asset_dict["name"]
    if Asset.find_by_name(name):
        error = f"Asset name: {name} already exists, must be unique."
        abort(HTTPStatus.CONFLICT, error, status="fail")
    asset = Asset(**asset_dict)
    db.session.add(asset)
    db.session.commit()
    response = jsonify(status="success", message=f"New asset added: {name}.")
    response.status_code = HTTPStatus.CREATED
    response.headers["Location"] = url_for("api.asset", name=name)
    return response


def retrieve_asset_list(page, per_page):
    pagination = Asset.query.paginate(page=page, per_page=per_page, error_out=False)
    response_data = marshal(pagination, pagination_model)
    response_data["links"] = _pagination_nav_links(pagination)
    response = jsonify(response_data)
    response.headers["Link"] = _pagination_nav_header_links(pagination)
    response.headers["Total-Count"] = pagination.total
    return response


def retrieve_asset(name):
    return Asset.query.filter_by(name=name.lower()).first_or_404(
        description=f"{name} not found in database."
    )


def update_asset(name, asset_dict):
    asset = Asset.find_by_name(name.lower())
    if asset:
        for k, v in asset_dict.items():
            setattr(asset, k, v)
        db.session.commit()
        message = f"'{name}' was successfully updated"
        response_dict = dict(status="success", message=message)
        return response_dict, HTTPStatus.OK
    try:
        valid_name = asset_name(name.lower())
    except ValueError as e:
        abort(HTTPStatus.BAD_REQUEST, str(e), status="fail")
    asset_dict["name"] = valid_name
    return create_asset(asset_dict)


def delete_asset(name):
    asset = Asset.query.filter_by(name=name.lower()).first_or_404(
        description=f"{name} not found in database."
    )
    db.session.delete(asset)
    db.session.commit()
    return "", HTTPStatus.NO_CONTENT


def _pagination_nav_links(pagination):
    nav_links = {}
    per_page = pagination.per_page
    this_page = pagination.page
    last_page = pagination.pages
    nav_links["self"] = url_for("api.asset_list", page=this_page, per_page=per_page)
    nav_links["first"] = url_for("api.asset_list", page=1, per_page=per_page)
    if pagination.has_prev:
        nav_links["prev"] = url_for(
            "api.asset_list", page=this_page - 1, per_page=per_page
        )
    if pagination.has_next:
        nav_links["next"] = url_for(
            "api.asset_list", page=this_page + 1, per_page=per_page
        )
    nav_links["last"] = url_for("api.asset_list", page=last_page, per_page=per_page)
    return nav_links


def _pagination_nav_header_links(pagination):
    url_dict = _pagination_nav_links(pagination)
    link_header = ""
    for rel, url in url_dict.items():
        link_header += f'<{url}>; rel="{rel}", '
    return link_header.strip().strip(",")
