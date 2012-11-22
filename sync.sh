#!/usr/bin/env bash
cd $(dirname $0)
host="zope@ode.makina-corpus.net"
w="/opt/minitage/zope/libertic.event-preprod"
for i in var/filestorage/Data.fs var/blobstorage/;do
    echo "rsync -azvP --exclude="*backup*" $host:$w/$i  $i(enter to coninue)"?;read
    rsync -azvP --exclude="*.old*" --exclude="*backup*" $host:$w/$i $i
done
./bin/zeoserver restart

# vim:set et sts=4 ts=4 tw=80:
