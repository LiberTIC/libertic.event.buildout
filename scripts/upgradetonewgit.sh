#!/usr/bin/env bash
cd $(dirname $0)/..
rm -rvf ../../minilays/*libertic.event*
ln -sf $PWD/*minilay ../../minilays/libertic.event
# vim:set et sts=4 ts=4 tw=80:
