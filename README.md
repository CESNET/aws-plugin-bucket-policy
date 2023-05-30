# aws-plugin-bucket-policy
AWS CLI plugin - bucket policy admin tool

## Installation

* Dependencies: python3-minimal python3-pip mandoc groff-base
    optionally: python3-venv
* Optionally start virtualenv: ```python3 -m venv venv; . venv/bin/activate```

* ```pip install poetry pytest awscli_plugin_endpoint```

* Build & Install aws-plugin-bucket-policy with poetry:
```python
git clone https://github.com/CESNET/aws-plugin-bucket-policy
cd aws-plugin-bucket-policy
poetry build
cd dist
tar -xvf aws-plugin-bucket-policy-X.Y.Z.tar.gz
```
```
pip install --user aws-plugin-bucket-policy-X.Y.Z/
```
or in virtualenv without ```--user```:
```
pip install aws-plugin-bucket-policy-X.Y.Z/
```

## Configuration
* aws config ```.aws/config```:
```python
[profile profile_name]
output = text
s3 =
    endpoint_url = <endpoint_url>
s3api =
    endpoint_url = <endpoint_url>
s3bucket-policy = 
    endpoint_url = <endpoint_url>

[plugins]
s3bucket-policy = aws_plugin_bucket_policy
endpoint = awscli_plugin_endpoint

```

* S3 credentials: ```.aws/credentials```:
```python
[profile_name]
aws_access_key_id = ...
aws_secret_access_key = ...
```
or using environment variables: AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY
(without ```--profile```, but ```--endpoint <endpoint_url>``` needed)

* For help run ```aws s3bucket-policy help``` and ```aws s3bucket-policy <subcommand> help```

## Examples:
```python
aws s3bucket-policy [--profile <profile_name>] get-policy --bucket <bucket_name>
aws s3bucket-policy [--profile <profile_name>] new-policy --bucket <bucket_name> --newpol-type share-w-user --newpol-spec tenant=<tenant_name>,user=<user_name>,action=rw
aws s3bucket-policy [--profile <profile_name>] new-policy --bucket <bucket_name> --newpol-type share-w-tenant --newpol-spec tenant=<tenant_name>,action=ro
aws s3bucket-policy [--profile <profile_name>] new-policy --bucket <bucket_name> --newpol-type ro-public
aws s3bucket-policy [--profile <profile_name>] put-policy --bucket <bucket_name> --policy <policy_file.json>
aws s3bucket-policy [--profile <profile_name>] delete-policy --bucket <bucket_name>
```
