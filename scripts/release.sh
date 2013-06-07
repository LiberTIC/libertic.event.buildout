#!/usr/bin/env bash
cd $(dirname $0)/..
branch=`git branch -q|grep "*"|sed  "s/* //"`
if [[ "$branch" = 'prod' ]];then
        branches="preprod master prod"
elif [[ "$branch" = 'preprod' ]];then
        branches="prod master preprod"
else
        branches="prod preprod master"
fi
for i in $branches;do 
    git checkout $i;git merge master;
done
# vim:set et sts=4 ts=4 tw=80:
