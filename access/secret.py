from typing import Optional
from kopf._core.actions.execution import Logger
from kubernetes.client.models.v1_secret import V1Secret
from kubernetes.client.rest import ApiException
from kubernetes import client, config
import traceback
import sys
from data.secret import Secret

config.load_incluster_config()
v1 = client.CoreV1Api()


def create_secret(body: V1Secret, logger: Logger) -> None:
    namespace = body.metadata['namespace']
    name = body.metadata['name']
    already_exists = False
    try:
        logger.debug("Creating secret")
        v1.create_namespaced_secret(namespace, body)
        logger.debug("Secret created")
    except ApiException as e:
        if e.reason == 'Conflict':
            logger.warn(
                f"{name} already exists in namespace {namespace}")
            already_exists = True
            return
        logger.error(e)
        traceback.print_exc()

    if already_exists:
        update_secret(body, logger)


def update_secret(body: V1Secret, logger: Logger) -> None:
    namespace = body.metadata['namespace']
    name = body.metadata['name']
    try:
        logger.debug("Patching secret")
        v1.patch_namespaced_secret(body.metadata['name'], namespace, body)
        logger.debug("Secret patched")
    except ApiException as e:
        if e.reason == 'Conflict':
            logger.warn(
                f"{name} already exists in namespace {namespace}")
            return
        logger.error(e)
        traceback.print_exc()


def delete_secret(name: str, namespace: str, logger: Logger) -> None:
    try:
        logger.debug("Deleting secret")
        v1.delete_namespaced_secret(name, namespace)
        logger.debug("Secret deleted")
    except ApiException as e:
        if e.reason == 'Not Found':
            logger.warn(
                f"{name} does not exist in namespace {namespace}")
            return
        logger.error(e)
        traceback.print_exc()


def get_secret(name: str, namespace: str, logger: Logger) -> Optional[V1Secret]:
    try:
        logger.debug("Reading secret")
        return v1.read_namespaced_secret(name, namespace)
    except ApiException as e:
        logger.error(e)
        traceback.print_exc()
