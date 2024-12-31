"""API-related constants."""

# API Version
API_VERSION = "v1"

# API Endpoints
API_PREFIX = "/api"
API_DOCS = "/docs"
API_SPEC = "/openapi.json"

# API Methods
GET = "GET"
POST = "POST"
PUT = "PUT"
DELETE = "DELETE"

# Status Codes
SUCCESS = 200
CREATED = 201
ACCEPTED = 202
NO_CONTENT = 204
BAD_REQUEST = 400
UNAUTHORIZED = 401
FORBIDDEN = 403
NOT_FOUND = 404
SERVER_ERROR = 500

# Headers
CONTENT_TYPE = "Content-Type"
AUTHORIZATION = "Authorization"
API_KEY = "X-API-Key"

# Content Types
JSON = "application/json"
FORM = "application/x-www-form-urlencoded"
MULTIPART = "multipart/form-data"
