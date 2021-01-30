from fractions import Fraction as frac
from typing import *


class Categories:
    def __init__(self, model):
        self._model = model

    def get_category(self, category: str) -> List:
        items = self._model.query.distinct(category)
        categories = [item.__getattribute__(category) for item in items]
        categories.insert(0, None)
        return categories


class TotalAreas:
    def __init__(self, items: List):
        self._items = items

    @property
    def gross_wall_area(self) -> float:
        area = frac("0")
        for item in self._items:
            area += frac(str(item.gross_wall_area))
        return round(float(area), 2)

    @property
    def wall_area_to_survey(self) -> float:
        area = frac("0")
        for item in self._items:
            area += frac(str(item.wall_area_to_survey))
        return round(float(area), 2)

    @property
    def wall_area_to_sale(self) -> float:
        area = frac("0")
        for item in self._items:
            area += frac(str(item.wall_area_to_sale))
        return round(float(area), 2)

    @property
    def area_left_to_sale(self) -> float:
        area = frac("0")
        for item in self._items:
            area += frac(str(item.wall_area_to_sale)) * frac(str(item.left_to_sale))
        return round(float(area), 2)
