from typing import *

from pymongo.collection import Collection
from pymongo.cursor import Cursor
from wtforms import StringField, IntegerField, FloatField, BooleanField, DateTimeField, SubmitField

from app import mongo


class RegistryStore:
    """ Concatenates custom registries with investments and workers. """

    def __init__(self, invest_id: int, username: str):
        self.invest_id = invest_id
        self.username = username

    @property
    def investments(self) -> Collection:
        """ Returns investment collection. """
        return mongo.db["investments"]

    def get_registry(self, registry_name: str) -> Dict:
        registry = self.investments.find_one(
            {"invest_id": self.invest_id, "registry_name": registry_name}
        )
        if isinstance(registry, dict):
            if self.username in registry.get("users", None):
                return registry
            raise ValueError("Registry with this name already exists. Use different name.")

    def add_registry_to_store(self, registry_name: str) -> None:
        if registry_name and not self.get_registry(registry_name):
            self.investments.insert_one(
                {
                    "invest_id": self.invest_id,
                    "registry_name": registry_name,
                    "schema": [],
                    "users": [self.username],
                }
            )

    @classmethod
    def get_user_registries(cls, invest_id: int, username: str) -> List[str]:
        registries = mongo.db.investments.find({"invest_id": invest_id, "users": {"$in": [username]}})
        return [item.get("registry_name") for item in registries]


class Registry(RegistryStore):
    """ Handles creating and managing custom registry. """

    def __init__(self, invest_id: int, username: str, registry_name: str):
        super().__init__(invest_id, username)
        self.invest_id = invest_id
        self.registry_name = registry_name
        self.collection_name = f"investment_{invest_id}_{registry_name}"
        self.add_registry_to_store(self.registry_name)

    @property
    def registry(self) -> Collection:
        """ Representation of custom registry in database. """
        return mongo.db[self.collection_name]

    @property
    def data_type_map(self):
        return {
            "string": StringField,
            "integer": IntegerField,
            "float": FloatField,
            "bool": BooleanField,
            "date": DateTimeField,
        }

    def get_schema(self) -> List:
        try:
            return self.get_registry(self.registry_name).get("schema", None)
        except AttributeError:
            return []

    def add_field(self, name: str, data_type: str, **options) -> None:
        """ Adds new field to registry schema. """
        field = {
            "name": name,
            "data_type": data_type,
            "options": options,
        }
        query = {"invest_id": self.invest_id, "registry_name": self.registry_name}
        push_username = {"$push": {"schema": field}}
        self.investments.update_one(query, push_username)

    def get_fields(self) -> List[str]:
        return [field["name"] for field in self.get_schema()]

    def get_form_fields(self) -> Dict:
        form_fields = {}
        for field in self.get_schema():
            name = field.get("name", None)
            data_type = field.get("data_type", None)
            data_type_cls = self.data_type_map.get(data_type, None)
            form_fields[name] = data_type_cls(name)
        form_fields["Submit"] = SubmitField("Submit")
        return form_fields

    def validate_data(self, data: Dict) -> Dict:
        result = {}
        for field in self.get_fields():
            result[field] = data.get(field)
        return result

    def add_item(self, data: Dict) -> None:
        """ Ads new item to registry. """
        self.registry.insert_one(self.validate_data(data))

    def get_items(self) -> Cursor:
        """ Gets all items from registry. """
        return self.registry.find({}, {"_id": 0})

    def add_user_to_registry(self, username: str) -> None:
        query = {"invest_id": self.invest_id, "registry_name": self.registry_name}
        push_username = {"$push": {"users": username}}
        self.investments.update_one(query, push_username)
