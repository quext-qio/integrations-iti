
FROM node:18-alpine as cdk
ARG AWS_DEFAULT_REGION
ARG AWS_ACCESS_KEY_ID
ARG AWS_SECRET_ACCESS_KEY
ARG AWS_SESSION_TOKEN
ENV PYTHONUNBUFFERED=1
ENV JSII_SILENCE_WARNING_UNTESTED_NODE_VERSION=true
WORKDIR /app
# Copy the CDK application code to the container
COPY . /app
RUN apk add --update --no-cache python3 git py3-pip && ln -sf python3 /usr/bin/python \
    && npm install -g aws-cdk \
    && pip3 install --no-cache --upgrade pip setuptools \
    && python3 -m venv /.env \
    && pip install --upgrade awscli
RUN source /.env/bin/activate
RUN pip install -r requirements.txt
CMD ["/bin/sh"]