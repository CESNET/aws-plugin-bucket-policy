# aws-plugin-bucket-policy
AWS CLI plugin - bucket policy admin tool

## Installation

* Dependencies: python3-minimal python3-pip mandoc groff-base
    optionally: python3-venv
* Optionally start virtualenv: ```python3 -m venv venv; . venv/bin/activate```

* ```pip install poetry pytest awscli_plugin_endpoint```

* Build & Install aws-plugin-bucket-policy with poetry:
```python
wget https://github.com/CESNET/aws-plugin-bucket-policy/archive/refs/heads/main.zip
unzip main.zip
cd aws-plugin-bucket-policy-main
poetry build
cd dist
tar -xvf aws_plugin_bucket_policy-X.Y.Z.tar.gz
```
```
pip install --user aws_plugin_bucket_policy-X.Y.Z/
```
or in virtualenv without ```--user```:
```
pip install aws_plugin_bucket_policy-X.Y.Z/
```

## Configuration
* aws config ```.aws/config```:
```python
[profile profile_name]
output = text
s3 =
    endpoint_url = ENDPOINT_URL
s3api =
    endpoint_url = ENDPOINT_URL
s3bucket-policy = 
    endpoint_url = ENDPOINT_URL

[plugins]
s3bucket-policy = aws_plugin_bucket_policy
endpoint = awscli_plugin_endpoint

```

* S3 credentials: ```.aws/credentials```:
```python
[profile_name]
aws_access_key_id = ***
aws_secret_access_key = ***
```
or using environment variables: AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY \
(without ```--profile```, but ```--endpoint ENDPOINT_URL``` needed)

## Help
* For help run ```aws s3bucket-policy help``` or ```aws s3bucket-policy SUBCOMMAND help```
* [Plugin commands manual on GitHub](https://github.com/CESNET/aws-plugin-bucket-policy/blob/main/docs/commands.md)

## Examples:
```python
aws s3bucket-policy --profile PROFILE_NAME get-policy --bucket BUCKET_NAME
aws s3bucket-policy --profile PROFILE_NAME new-policy --bucket BUCKET_NAME --newpol-type share-w-user --newpol-spec tenant=TENANT_NAME,user=USER_NAME,action=rw
aws s3bucket-policy --profile PROFILE_NAME new-policy --bucket BUCKET_NAME --newpol-type share-w-tenant --newpol-spec tenant=TENANT_NAME,action=ro
aws s3bucket-policy --profile PROFILE_NAME new-policy --bucket BUCKET_NAME --newpol-type ro-public
aws s3bucket-policy --profile PROFILE_NAME put-policy --bucket BUCKET_NAME --policy POLICY_FILE.json
aws s3bucket-policy --profile PROFILE_NAME delete-policy --bucket BUCKET_NAME
```

## Docker way:
* `Dockerfile` based on ubuntu:jammy
* S3 credentials should be defined in `S3_env` as AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables:
  (see `S3_env.template` file)
```python
AWS_ACCESS_KEY_ID=***
AWS_SECRET_ACCESS_KEY=***
```
* Usage examples:
```python
docker build -t s3bucket-policy .
docker run -it --rm -u awscli --env-file=S3_env --name s3bucket-policy s3bucket-policy --endpoint ENDPOINT_URL get-policy --bucket BUCKET_NAME
docker run -it --rm -u awscli --env-file=S3_env --name s3bucket-policy s3bucket-policy --endpoint ENDPOINT_URL help
docker run -it --rm -u awscli --env-file=S3_env --name s3bucket-policy s3bucket-policy --endpoint ENDPOINT_URL new-policy help
docker run -it --rm -u awscli --env-file=S3_env --name s3bucket-policy s3bucket-policy --endpoint ENDPOINT_URL new-policy --bucket BUCKET_NAME --newpol-type share-w-tenant --newpol-spec tenant=TENANT_NAME,action=ro
```
