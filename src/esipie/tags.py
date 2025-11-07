from esipie.esi_operation import EsiOperation


class EsiTag:
    """
    API Tag Wrapper, providing access to Operations within a tag
    Assets, Characters, etc.
    """

    def __init__(self, operation, api) -> None:
        self._oi = operation._oi
        self._operations = operation._operations
        self.api = api

    def __getattr__(self, name: str) -> EsiOperation:
        if name not in self._operations:
            raise AttributeError(
                f"Operation '{name}' not found in tag '{self._oi}'. "
                f"Available operations: {', '.join(sorted(self._operations.keys()))}"
            )
        return EsiOperation(self._operations[name], self.api)
