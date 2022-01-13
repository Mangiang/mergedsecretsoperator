from kubernetes import client
from kopf._core.actions.execution import Logger
from data.secret import Secret
from data.mergedsecret import crd_group, crd_version, crd_name


def get_all_merged_secrets(logger: Logger, namespace="*") -> list[Secret]:
    return client.CustomObjectsApi().list_cluster_custom_object(
        group=crd_group, version=crd_version, plural=crd_name)
