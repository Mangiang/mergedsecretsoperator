# Merged Secrets Operator

A simple Operator used to create secrets based on other secrets

## Usage

1. Apply the manifests:
    1. CustomResourceDefinitions: `kubectl apply -f manifests/crds`
    1. RBAC: `kubectl apply -f manifests/rbac`
    1. Run the operator
        * Either execute in your cluster: `python -m kopf run app.py --verbose`
        * Or use the image in your cluster `docker pull ghcr.io/mangiang/mergedsecretsoperator:latest`
        * Or use the deployment manifest : `kubectl apply -f manifests/operator`
1. See the `test` folder for examples
    1. `mergedsecret-test-source.yaml` is the base MergedSecret and will create a secret
    1. `mergedsecret-test.yaml` is the merged secret and will merge both its values and the secret from `mergedsecret-test-source.yaml`

## Links
 * Okteto
    * https://okteto.com/docs/reference/manifest/
 * Kopf
    * https://github.com/nolar/kopf
    * https://kopf.readthedocs.io/en/stable/walkthrough/starting/