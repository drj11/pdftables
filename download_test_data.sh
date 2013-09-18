#!/bin/sh

git clone https://bitbucket.org/scraperwikids/pdftables-test-data fixtures/

# get EU ground truth dataset
wget http://www.tamirhassan.com/files/eu-dataset-20130324.zip -O fixtures/eu.zip
unzip fixtures/eu.zip -d fixtures
rm fixtures/eu.zip

