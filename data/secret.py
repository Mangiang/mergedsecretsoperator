from typing import Any, Optional
from kopf._core.actions.execution import Logger


class Secret:
    def __init__(self, meta: Any, spec: dict[str, dict[str, str]], logger: Logger) -> 'Secret':
        from kubernetes import client
        self.body = client.V1Secret()
        self.body.api_version = 'v1'
        self.body.data = {}
        self.body.kind = 'Secret'
        self.body.metadata = {
            'name': meta['name'],
            'namespace': meta['namespace']
        }
        if 'labels' in meta:
            self.body.metadata['labels'] = {
                key: val for key, val in meta['labels'].items()}
        if 'annotations' in meta:
            self.body.metadata['annotations'] = {
                key: val for key, val in meta['annotations'].items()}
        self.body.type = 'Opaque'
        self.depends_on = []
        self.spec = spec
        self.logger = logger

    def add_values(self, values: dict[str, str]) -> None:
        for val in values:
            self.body.data[val] = values[val]

    def add_valuesFrom(self, values: dict[str, str]):
        from access.secret import get_secret
        for val in values:
            self.depends_on.append(f"{val['name']}.{val['namespace']}")
            other_secret = get_secret(
                val['name'], val['namespace'], self.logger)
            if other_secret:
                new_key = val['newKey'] if 'newKey' in val else val['key']
                self.body.data[new_key] = other_secret.data[val['key']]

    def update_data(self, spec: Optional[dict[str, dict[str, str]]] = None) -> 'Secret':
        if spec:
            self.spec = spec

        if 'values' in self.spec:
            self.add_values(self.spec['values'])
        if 'valuesFrom' in self.spec:
            self.add_valuesFrom(self.spec['valuesFrom'])

        return self

    def create(self, logger: Logger) -> None:
        from access.secret import create_secret
        create_secret(self.body, self.logger)

    def update(self, logger: Logger) -> None:
        from access.secret import update_secret
        self.update_data()
        update_secret(self.body, self.logger)
