#!/usr/bin/env bash

docker build \
    -f dockerfile \
    -t "fhrozen/py-discord:client" .
