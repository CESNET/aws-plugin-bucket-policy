
FROM ubuntu:jammy

MAINTAINER Tomas Hlava <hlava@cesnet.cz>

ENV TERM=xterm DEBIAN_FRONTEND=noninteractive LANG=en_US.utf8 LC_ALL=en_US.UTF-8

# update and install utilities:
ARG FORCE_UPDATE=no
RUN apt-get update && apt-get upgrade -y
RUN apt-get install --no-install-recommends --no-install-suggests -y \
    locales tzdata wget unzip \
    python3-minimal python3-pip python3-venv less mandoc groff-base \
  && localedef -i en_US -c -f UTF-8 -A /usr/share/locale/locale.alias en_US.UTF-8

# add non-root user:
ENV USER=awscli
RUN addgroup --gid 1000 $USER \
  && adduser --uid 1000 --gid 1000 --disabled-password --gecos "" $USER

USER $USER
WORKDIR /home/$USER
ENV PATH=/home/$USER/.local/bin:$PATH

# install python things:
RUN pip install --upgrade pip setuptools wheel awscli

# iterfzf support (can be disabled by 'docker build' with '--build-arg NOFZF=yes'):
ARG NOFZF
RUN [ -z "$NOFZF" ] && pip install iterfzf && sed -i '/if proc is None or proc.wait()/,/return None$/d' .local/lib/$(readlink $(which python3))/site-packages/iterfzf/__init__.py || /bin/true

# install aws-plugin-bucket-policy
RUN pip install --upgrade aws-plugin-bucket-policy

# generate aws config with plugin enabled as "s3bucket-policy" command:
RUN mkdir -p .aws && { grep -E '^\[plugins\]$' .aws/config > /dev/null || echo "[plugins]"; echo "s3bucket-policy = aws_plugin_bucket_policy"; } >> .aws/config

ENTRYPOINT ["aws", "s3bucket-policy"]

# Usage examples:
# docker build -t s3bucket-policy .
# docker run -it --rm -u awscli --env-file=S3_env --name s3bucket-policy s3bucket-policy --endpoint ENDPOINT get-policy --bucket BUCKET_NAME
# docker run -it --rm -u awscli --env-file=S3_env --name s3bucket-policy s3bucket-policy --endpoint ENDPOINT help
# docker run -it --rm -u awscli --env-file=S3_env --name s3bucket-policy s3bucket-policy --endpoint ENDPOINT new-policy help
# docker run -it --rm -u awscli --env-file=S3_env --name s3bucket-policy s3bucket-policy --endpoint ENDPOINT new-policy --bucket BUCKET_NAME --newpol-type share-w-tenant --newpol-spec tenant=TENANT_NAME,action=ro
