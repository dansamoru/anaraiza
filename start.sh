#!/bin/bash
cd /opt/anaraiza
docker build -t parser .
docker run -d --restart=always parser
