#!/usr/bin/env bash
cd $(dirname $0)/..
for i in prod preprod master;do 
    git checkout $i;git merge master;
done
# vim:set et sts=4 ts=4 tw=80:
