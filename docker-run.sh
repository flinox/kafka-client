#!/bin/bash
cd container

docker build -t flinox/kafka-client:latest .

docker run --rm -it --hostname kafka-client --name kafka-client \
--mount type=bind,source="$(pwd)"/_keys,target=/app/_keys/ \
--mount type=bind,source="$(pwd)"/python,target=/app/python/ \
--mount type=bind,source="$(pwd)"/shell,target=/app/shell/ \
-p 8080:8080 \
--security-opt label=disable \
flinox/kafka-client:latest \
/bin/bash

cd ..