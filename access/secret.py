from enum import Enum
from typing import Optional, Union
from kopf._core.actions.execution import Logger
from kubernetes.client.models.v1_secret import V1Secret
from kubernetes.client.rest import ApiException
from kubernetes import client, config
import traceback
import sys
from data.secret import Secret

config.load_incluster_config()
v1 = client.CoreV1Api()


class SecretOperationResult(Enum):
    OK = 0
    ALREADY_EXISTS = 1
    DOES_NOT_EXIST = 2
    OTHER_ERROR = 3


def create_secret(body: V1Secret, logger: Logger) -> SecretOperationResult:
    namespace = body.metadata['namespace']
    name = body.metadata['name']
    already_exists = False
    try:
        logger.debug("Creating secret")
        v1.create_namespaced_secret(namespace, body)
        logger.debug("Secret created")
        return SecretOperationResult.OK
    except ApiException as e:
        if e.reason == 'Conflict':
            logger.warn(
                f"{name} already exists in namespace {namespace}")
            already_exists = True
            return SecretOperationResult.ALREADY_EXISTS
        logger.error(e)
        traceback.print_exc()
    return SecretOperationResult.OTHER_ERROR

    if already_exists:
        update_secret(body, logger)


def update_secret(body: V1Secret, logger: Logger) -> SecretOperationResult:
    namespace = body.metadata['namespace']
    name = body.metadata['name']
    try:
        logger.debug("Patching secret")
        v1.patch_namespaced_secret(body.metadata['name'], namespace, body)
        logger.debug("Secret patched")
        return SecretOperationResult.OK
    except ApiException as e:
        if e.reason == 'Conflict':
            logger.warn(
                f"{name} already exists in namespace {namespace}")
            return SecretOperationResult.ALREADY_EXISTS
        if e.reason == 'Not Found':
            logger.warn(
                f"{name} does not exist in namespace {namespace} it will be re-created")
            return SecretOperationResult.DOES_NOT_EXIST
        logger.error(e)
        traceback.print_exc()
    return SecretOperationResult.OTHER_ERROR


def delete_secret(name: str, namespace: str, logger: Logger) -> SecretOperationResult:
    try:
        logger.debug("Deleting secret")
        v1.delete_namespaced_secret(name, namespace)
        logger.debug("Secret deleted")
        return SecretOperationResult.OK
    except ApiException as e:
        if e.reason == 'Not Found':
            logger.warn(
                f"{name} does not exist in namespace {namespace}")
            return SecretOperationResult.DOES_NOT_EXIST
        logger.error(e)
        traceback.print_exc()
    return SecretOperationResult.OTHER_ERROR


def get_secret(name: str, namespace: str, logger: Logger) -> Union[Optional[V1Secret], SecretOperationResult]:
    try:
        logger.debug("Reading secret")
        return v1.read_namespaced_secret(name, namespace)
    except ApiException as e:
        logger.error(e)
        traceback.print_exc()
    return SecretOperationResult.OTHER_ERROR
