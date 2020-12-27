from typing import *
from app import db

from fractions import Fraction as frac
from wtforms.validators import ValidationError


def is_nan(x):
    return x != x


def validate_walls(data: Dict) -> Dict:
    """ Validates values from inputted Dict and returns it when no ValidationError occurs. """

    data = check_field_type(data, "wall_width", int)
    for field in ["wall_length", "floor_ord", "ceiling_ord"]:
        data = check_field_type(data, field, float)
        check_not_nan(data[field])
    return data


def validate_holes(data: Dict) -> Dict:
    for field in ["width", "height"]:
        data = check_field_type(data, field, float)
        check_not_nan(data[field])
    data = check_field_type(data, "amount", int)
    return data


def validate_processing(wall: db.Model, data: Dict) -> Dict:
    data = check_field_type(data, "year", int)
    data = check_field_type(data, "month", str)
    data = check_field_type(data, "done", float)
    if data["year"] in [0, None]:
        raise ValidationError("Value of 'year' can not be '0' or 'None'!")
    if data["month"] == "nan":
        raise ValidationError("Value of 'month' can not be 'NaN'!")
    check_not_nan(data["done"])
    if data["done"] < 0:
        raise ValidationError("done values must be greater than 0!")
    data = validate_done_attr_while_adding(wall, data)
    return data


def check_field_type(data: Dict, field: str, field_type: Type) -> Dict:
    try:
        value = field_type(data.get(field, None))
    except (ValueError, TypeError):
        raise ValidationError(
            "Value of '{}' must be '{}'!".format(field, field_type.__name__)
        )
    else:
        data[field] = value
        return data


def check_not_nan(field: float) -> None:
    if is_nan(field):
        raise ValidationError("Value of '{}' can not be 'NaN'!".format(field))


def check_field_exists(data: Dict, field: str) -> Any:
    try:
        data = check_field_type(data, field, int)
    except ValidationError:
        return None
    else:
        return data[field]


def validate_done_attr_while_adding(wall: db.Model, data: Dict) -> Dict:
    done = data.get("done")
    if done:
        if float(wall.left_to_sale) < float(done):
            data["done"] = float(wall.left_to_sale)
    return data


def validate_done_attr_while_editing(
    wall: db.Model, processing: db.Model, data: Dict
) -> Dict:
    done = data.get("done")
    if done:
        left_to_sale = frac(str(wall.left_to_sale))
        left_to_sale += frac(str(processing.done))
        if float(left_to_sale) < float(done):
            data["done"] = float(left_to_sale)
    return data
