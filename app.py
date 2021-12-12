from logging import log
import kopf
from kopf._core.actions.execution import Logger
from data.secret import Secret
from access.secret import create_secret, delete_secret, get_secret, update_secret
from utils.utils import print_info, get_namespace

context = 'mergedsecrets.app'

secrets: dict[str, Secret] = {}
secrets_dependency: dict[str, list[Secret]] = {}

crd_group = 'arthur-joly.fr'
crd_version = 'v1'
crd_name = 'mergedsecrets'


@kopf.on.resume(crd_group, crd_version, crd_name)
@kopf.on.create(crd_group, crd_version, crd_name)
def create(spec, name, meta, status, logger: Logger, **kwargs):
    full_name = f"{name}.{meta['namespace']}"
    secrets[full_name] = Secret(
        name, get_namespace(meta), spec, logger).update_data()

    for dependency in secrets[full_name].depends_on:
        if dependency not in secrets_dependency:
            secrets_dependency[dependency] = [secrets[full_name]]
        else:
            secrets_dependency[dependency].append(secrets[full_name])

    secrets[full_name].create(logger)
    logger.debug(f"Created {full_name}")

    if full_name in secrets_dependency:
        logger.debug(f"{full_name} detected in secrets_dependency")
        for dep in secrets_dependency[full_name]:
            logger.debug(
                f"Updating {dep.body.metadata['name']}.{dep.body.metadata['namespace']}")
            dep.update_data().update(logger)

    for key in secrets_dependency:
        logger.debug(
            f"dep on {key}: [{','.join(sec.body.metadata['name'] for sec in secrets_dependency[key])}]")


@kopf.on.update(crd_group, crd_version, crd_name)
def update(spec, name, meta, status, logger: Logger, **kwargs):
    full_name = f"{name}.{meta['namespace']}"
    if full_name not in secrets:
        create(spec, name, meta, status, logger)
        return

    secrets[full_name].update_data(spec).update(logger)
    logger.debug(f"Updated {full_name}")


@kopf.on.delete(crd_group, crd_version, crd_name)
def delete(spec, name, meta, status, logger: Logger, **kwargs):
    full_name = f"{name}.{meta['namespace']}"
    delete_secret(name, get_namespace(meta), logger)
    logger.debug(f"Deleted {full_name}")
