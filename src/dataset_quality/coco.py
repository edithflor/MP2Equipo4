"""Contrato COCO detection del MP1, sin acceso a archivos, BD ni almacenamiento.

La estructura y las referencias se validan aquí. La geometría defectuosa se
conserva para los analizadores: aceptar el contrato no significa aprobar calidad.
"""

from typing import Annotated, Self

from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator, model_validator
from pydantic_core import InitErrorDetails

Identifier = Annotated[int, Field(strict=True, ge=0)]
Dimension = Annotated[int, Field(strict=True, gt=0)]
Number = Annotated[float, Field(strict=True, allow_inf_nan=False)]
Text = Annotated[str, Field(strict=True, min_length=1, pattern=r"\S")]


class CocoModel(BaseModel):
    # Extensiones COCO se conservan; los campos conocidos sí se validan estrictamente.
    model_config = ConfigDict(extra="allow", strict=True)


class CocoInfo(CocoModel):
    description: str = ""
    version: str = ""
    year: Identifier | None = None
    date_created: str | None = None


class CocoLicense(CocoModel):
    id: Identifier
    name: str
    url: str = ""


class CocoImage(CocoModel):
    id: Identifier
    file_name: Text
    width: Dimension
    height: Dimension
    date_captured: str | None = None


class CocoCategory(CocoModel):
    id: Identifier
    name: Text
    supercategory: str = "object"


class CocoAnnotation(CocoModel):
    id: Identifier
    image_id: Identifier
    category_id: Identifier
    bbox: Annotated[list[Number], Field(min_length=4, max_length=4)]
    area: Number
    iscrowd: Annotated[int, Field(strict=True, ge=0, le=1)] = 0
    # MP1 exporta [] (detection). Polígonos también son compatibles.
    segmentation: list[list[Number]] = Field(default_factory=list)


class CocoDataset(CocoModel):
    """Entrada pública para F2-02: model_validate(dict) o model_validate_json(texto)."""

    info: CocoInfo | None = None
    licenses: list[CocoLicense] = Field(default_factory=list)
    images: list[CocoImage]
    categories: list[CocoCategory]
    annotations: list[CocoAnnotation]

    @field_validator("images", "categories", "annotations", "licenses")
    @classmethod
    def unique_ids(cls, records):
        seen: set[int] = set()
        errors: list[InitErrorDetails] = []
        for index, record in enumerate(records):
            if record.id in seen:
                errors.append(
                    InitErrorDetails(
                        type="value_error",
                        loc=(index, "id"),
                        input=record.id,
                        ctx={"error": ValueError(f"ID duplicado: {record.id}")},
                    )
                )
            seen.add(record.id)
        if errors:
            raise ValidationError.from_exception_data(cls.__name__, errors)
        return records

    @model_validator(mode="after")
    def existing_references(self) -> Self:
        image_ids = {image.id for image in self.images}
        category_ids = {category.id for category in self.categories}
        errors: list[InitErrorDetails] = []
        for index, annotation in enumerate(self.annotations):
            for field, known in (("image_id", image_ids), ("category_id", category_ids)):
                value = getattr(annotation, field)
                if value not in known:
                    errors.append(
                        InitErrorDetails(
                            type="value_error",
                            loc=("annotations", index, field),
                            input=value,
                            ctx={"error": ValueError(f"Referencia inexistente: {field}={value}")},
                        )
                    )
        if errors:
            raise ValidationError.from_exception_data(type(self).__name__, errors)
        return self
