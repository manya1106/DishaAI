from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field


class BaseSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")


class ErrorDetail(BaseSchema):
    code: str = Field(..., description="Machine-readable error code")
    message: str = Field(..., description="Human-readable explanation of error")
    request_id: Optional[str] = Field(None, description="Request trace ID if present")


class ErrorResponse(BaseSchema):
    error: ErrorDetail


class HealthResponse(BaseSchema):
    status: str = Field(..., example="ok")
    version: str = Field(..., example="1.0.0")
    data_mode: str = Field(..., example="snapshot")
    db: str = Field(..., example="connected")
    llm: str = Field(..., example="configured")


class Centroid(BaseSchema):
    lat: float
    lng: float


class GeoJSONPolygonGeometry(BaseSchema):
    type: str = "Polygon"
    coordinates: List[List[List[float]]]


class GeoJSONFeature(BaseSchema):
    type: str = "Feature"
    geometry: GeoJSONPolygonGeometry
    properties: dict = Field(default_factory=dict)


class GeoJSONFeatureCollection(BaseSchema):
    type: str = "FeatureCollection"
    features: List[GeoJSONFeature]
