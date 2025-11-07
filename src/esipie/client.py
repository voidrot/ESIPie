from aiopenapi3 import OpenAPI
from aiopenapi3.request import OperationIndex

from esipie.stubs import EsiClientStub
from esipie.tags import EsiTag


class EsiClient(EsiClientStub):
    def __init__(self, api: OpenAPI) -> None:
        self.api = api
        self._tags = set(api._operationindex._tags.keys())

    def __getattr__(self, tag: str) -> EsiTag | OperationIndex:
        # underscore returns the raw aiopenapi3 client
        if tag == "_":
            return self.api._operationindex

        # convert pythonic Planetary_Interaction to Planetary Interaction
        if "_" in tag:
            tag = tag.replace("_", " ")

        if tag in set(self.api._operationindex._tags.keys()):
            return EsiTag(self.api._operationindex._tags[tag], self.api)

        raise AttributeError(f"Tag '{tag}' not found. Available tags: {', '.join(sorted(self._tags))}")
