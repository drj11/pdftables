#!/bin/sh

for pdf in fixtures/sample_data/*.pdf
do
  printf -- "---** %s **---\n" "$pdf"
  pdftables-render "$pdf"
done
