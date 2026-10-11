"""Helpers for reading the error messages the OpenAPI schema documents."""

from api.routers import api


def documented_messages(method: str, path: str, status: int) -> set[str]:
    """Return the `detail` examples the OpenAPI schema lists for `status` on `method` `path`."""
    schema = api.get_openapi_schema()
    response = schema['paths'][path][method]['responses'][status]
    ref = response['content']['application/json']['schema']['$ref']
    component = schema['components']['schemas'][ref.rsplit('/', 1)[-1]]
    return set(component['properties']['detail']['examples'])


def documented_statuses(method: str, path: str) -> set[int]:
    """Return every status code the OpenAPI schema declares for `method` `path`."""
    return set(api.get_openapi_schema()['paths'][path][method]['responses'])
