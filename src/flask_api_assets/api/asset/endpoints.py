"""API endpoint definitions for /assets namespace."""
from http import HTTPStatus

from flask_restx import Namespace, Resource

from flask_api_assets.api.asset.dto import (
    create_asset_reqparser,
    update_asset_reqparser,
    pagination_reqparser,
    asset_model,
    pagination_links_model,
    pagination_model,
)
from flask_api_assets.api.asset.business import (
    create_asset,
    retrieve_asset_list,
    retrieve_asset,
    update_asset,
    delete_asset,
)

asset_ns = Namespace(name="assets", validate=True)
asset_ns.models[asset_model.name] = asset_model
asset_ns.models[pagination_links_model.name] = pagination_links_model
asset_ns.models[pagination_model.name] = pagination_model


@asset_ns.route("", endpoint="asset_list")
@asset_ns.response(int(HTTPStatus.BAD_REQUEST), "Validation error.")
@asset_ns.response(int(HTTPStatus.UNAUTHORIZED), "Unauthorized.")
@asset_ns.response(int(HTTPStatus.INTERNAL_SERVER_ERROR), "Internal server error.")
class AssetList(Resource):
    """Handles HTTP requests to URL: /assets."""

    @asset_ns.response(HTTPStatus.OK, "Retrieved asset list.", pagination_model)
    @asset_ns.expect(pagination_reqparser)
    def get(self):
        """Retrieve a list of assets."""
        request_data = pagination_reqparser.parse_args()
        page = request_data.get("page")
        per_page = request_data.get("per_page")
        return retrieve_asset_list(page, per_page)

    @asset_ns.response(int(HTTPStatus.CREATED), "Added new asset.")
    @asset_ns.response(int(HTTPStatus.FORBIDDEN), "Administrator token required.")
    @asset_ns.response(int(HTTPStatus.CONFLICT), "Asset name already exists.")
    @asset_ns.expect(create_asset_reqparser)
    def post(self):
        """Create a asset."""
        asset_dict = create_asset_reqparser.parse_args()
        return create_asset(asset_dict)


@asset_ns.route("/<name>", endpoint="asset")
@asset_ns.param("name", "Asset name")
@asset_ns.response(int(HTTPStatus.BAD_REQUEST), "Validation error.")
@asset_ns.response(int(HTTPStatus.NOT_FOUND), "Asset not found.")
@asset_ns.response(int(HTTPStatus.UNAUTHORIZED), "Unauthorized.")
@asset_ns.response(int(HTTPStatus.INTERNAL_SERVER_ERROR), "Internal server error.")
class Asset(Resource):
    """Handles HTTP requests to URL: /assets/{name}."""

    @asset_ns.response(int(HTTPStatus.OK), "Retrieved asset.", asset_model)
    @asset_ns.marshal_with(asset_model)
    def get(self, name):
        """Retrieve a asset."""
        return retrieve_asset(name)

    @asset_ns.response(int(HTTPStatus.OK), "Asset was updated.", asset_model)
    @asset_ns.response(int(HTTPStatus.CREATED), "Added new asset.")
    @asset_ns.response(int(HTTPStatus.FORBIDDEN), "Administrator token required.")
    @asset_ns.expect(update_asset_reqparser)
    def put(self, name):
        """Update a asset."""
        asset_dict = update_asset_reqparser.parse_args()
        return update_asset(name, asset_dict)

    @asset_ns.response(int(HTTPStatus.NO_CONTENT), "Asset was deleted.")
    @asset_ns.response(int(HTTPStatus.FORBIDDEN), "Administrator token required.")
    def delete(self, name):
        """Delete a asset."""
        return delete_asset(name)
