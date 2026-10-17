
from pydantic import BaseModel, ConfigDict, Field


class BaseSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")


class ErrorDetail(BaseSchema):
    code: str = Field(..., description="Machine-readable error code")
    message: str = Field(..., description="Human-readable explanation of error")
    request_id: str | None = Field(None, description="Request trace ID if present")


class ErrorResponse(BaseSchema):
    error: ErrorDetail


class HealthResponse(BaseSchema):
    status: str = Field(..., json_schema_extra={"example": "ok"})
    version: str = Field(..., json_schema_extra={"example": "1.0.0"})
    data_mode: str = Field(..., json_schema_extra={"example": "snapshot"})
    db: str = Field(..., json_schema_extra={"example": "connected"})
    llm: str = Field(..., json_schema_extra={"example": "configured"})


class Centroid(BaseSchema):
    lat: float
    lng: float


class GeoJSONPolygonGeometry(BaseSchema):
    type: str = "Polygon"
    coordinates: list[list[list[float]]]


class GeoJSONFeature(BaseSchema):
    type: str = "Feature"
    geometry: GeoJSONPolygonGeometry
    properties: dict = Field(default_factory=dict)


class GeoJSONFeatureCollection(BaseSchema):
    type: str = "FeatureCollection"
    features: list[GeoJSONFeature]
