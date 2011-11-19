#!/bin/sh
cd ./invoicer
../bin/django makemessages -e .html -e .txt -a -l it
cd ..
