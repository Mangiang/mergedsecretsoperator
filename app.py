import kopf
from kopf._core.actions.execution import Logger
from data.secret import Secret
from access.secret import delete_secret
from access.mergedsecret import get_all_merged_secrets
from utils.utils import get_namespace
from data.mergedsecret import crd_group, crd_version, crd_name
import json 
context = 'mergedsecrets.app'

secrets: dict[str, Secret] = {}
secrets_dependency: dict[str, set[Secret]] = {}


@kopf.on.startup()
def startup(logger, **kwargs):
    merged_secrets = get_all_merged_secrets(logger)
    if merged_secrets:
        for secret in merged_secrets['items']:
            meta = secret['metadata']
            full_name = f"{meta['name']}.{meta['namespace']}"
            if full_name not in secrets:
                secrets[full_name] = Secret(meta, secret['spec'], logger)


@kopf.on.resume(crd_group, crd_version, crd_name)
@kopf.on.create(crd_group, crd_version, crd_name)
def create(spec, name, meta, status, logger: Logger, **kwargs):
    full_name = f"{name}.{meta['namespace']}"
    secrets[full_name] = Secret(meta, spec, logger).update_data()

    for dependency in secrets[full_name].depends_on:
        if dependency not in secrets_dependency:
            secrets_dependency[dependency] = set([secrets[full_name]])
        else:
            secrets_dependency[dependency].add(secrets[full_name])

    secrets[full_name].apply(logger)
    logger.debug(f"Created {full_name}")

    if full_name in secrets_dependency:
        logger.debug(f"{full_name} detected in secrets_dependency")
        for dep in secrets_dependency[full_name]:
            logger.debug(
                f"Updating {dep.body.metadata['name']}.{dep.body.metadata['namespace']}")
            dep.update_data().apply(logger)


@kopf.on.update(crd_group, crd_version, crd_name)
def update(spec, name, meta, status, logger: Logger, **kwargs):
    full_name = f"{name}.{meta['namespace']}"
    if full_name not in secrets:
        create(spec, name, meta, status, logger)
        return

    # Update all dependencies
    if full_name in secrets_dependency:
        for secret in secrets_dependency[full_name]:
            dep.update_data().apply(logger)

    secrets[full_name].update_data(spec).apply(logger)
    logger.debug(f"Updated {full_name}")


@kopf.on.delete(crd_group, crd_version, crd_name)
def delete(spec, name, meta, status, logger: Logger, **kwargs):
    full_name = f"{name}.{meta['namespace']}"
    delete_secret(name, get_namespace(meta), logger)
    del secrets[full_name]
    for dep_key in secrets_dependency:
        if full_name in secrets_dependency[dep_key]:
            secrets_dependency[dep_key].remove(full_name)
    logger.debug(f"Deleted {full_name}")
