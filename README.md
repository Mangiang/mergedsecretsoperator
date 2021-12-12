# Merged Secrets Operator

A simple Operator used to create secrets based on other secrets

## Usage

1. Run the operator: `python -m kopf run app.py --verbose`
1. See the `test` folder
    1. `mergedsecret-test-source.yaml` is the base MergedSecret and will create a secret
    1. `mergedsecret-test.yaml` is the merged secret and will merge both its values and the secret from `mergedsecret-test-source.yaml`

## Links
 * Okteto
    * https://okteto.com/docs/reference/manifest/
 * Kopf
    * https://github.com/nolar/kopf
    * https://kopf.readthedocs.io/en/stable/walkthrough/starting/