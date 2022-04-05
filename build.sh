#!/bin/bash

set -e

docker build -t angrygoat/baysiebins . &&
docker push angrygoat/baysiebins

