#!/usr/bin/env bash
cd $(dirname $0)/..
PROJECT="libertic.event"
GITORIOUS=""
GDOT="."
IMPORT_URL="ssh://git@github.com/LiberTIC/libertic.event.buildout.git"
if [[ $(echo "$IMPORT_URL"|sed -re "s/.*gitorious.*/match/g") == "match" ]];then
    GITORIOUS="1"
    GDOT="-"
fi
GPROJECT="${PROJECT//\./${GDOT}}"
cd $(dirname $0)/..
[[ ! -d t ]] && mkdir t
rm -rf t/*
tar xzvf $(ls -1t ~/cgwb/$PROJECT*z) -C t
files="
.gitignore
bootstrap.py
buildout-dev.cfg
buildout-prod.cfg
minitage.buildout-dev.cfg
minitage.buildout-prod.cfg
LINK_TO_REGENERATE.html
README.*
minilays/
"
for f in $files;do
    rsync -aKzv t/$f $f
done
rm -rf  t/src/*/src/libertic/event/skins/libertic_event_custom/.empty
rm -rf  t/src/*/src/libertic/event/skins/libertic_event_custom/CONTENT.txt
rm -rf  t/src/*/src/libertic/event/skins/libertic_event_custom/base_properties.props
rm -rf  t/src/*/src/libertic/event/skins/libertic_event_custom/favicon.ico
rm -rf  t/src/*/src/libertic/event/skins/libertic_event_custom/logo.jpg
rsync -aKzv  --exclude=versions.cfg t/etc/ etc/
rsync -aKzv  t/etc/ etc/
policy="tests/base.py
upgrades/
interfaces.py
configure.zcml
tests/
testing.py
profiles/default/metadata.xml"
policy_folder="src.mrdeveloper/$PROJECT.policy"
if [[ ! -e $policy_folder ]];then
    policy_folder="src/$PROJECT.policy"
fi
if [[ ! -e $policy_folder ]];then
    policy_folder="src/$PROJECT"
fi
for i in $policy;do
    rsync -azKv t/src/$PROJECT/src/${PROJECT/\./\/}/$i src.mrdeveloper/$PROJECT/src/${PROJECT/\./\/}/$i
done
rsync -azKv t/src/$PROJECT/setup.py src.mrdeveloper/$PROJECT/setup.py
rsync -azKv t/src/$PROJECT/RE*.mrdeveloper/$PROJECT/RE*
EGGS_IMPORT_URL="${IMPORT_URL//\/$GPROJECT${GDOT}buildout\.git}"
sed -re "/\[sources\]/{
        a $PROJECT =  git $EGGS_IMPORT_URL/$GPROJECT.git
}" -i  etc/project/sources.cfg
sed -re "s:(src/)?$PROJECT::g" -i etc/project/$PROJECT.cfg
sed -re "/auto-checkout \+=/{
        a \    $PROJECT
        a \    plone.app.async
        a \    collective.cron
}"  -i etc/project/sources.cfg
sed -re "/ Pillow/{
        a \    $PROJECT
}"  -i etc/project/$PROJECT.cfg
sed -re "/zcml\+?=/{
        a \    $PROJECT
}"  -i etc/project/$PROJECT.cfg
sed -re "s/.*:default/    ${PROJECT}:default/g" -i  etc/project/$PROJECT.cfg
sed -re "s/(extends=.*)/\1 etc\/sys\/settings-prod.cfg/g" -i buildout-prod.cfg
sed -re "/\[buildout\]/ {
aallow-hosts = \${mirrors:allow-hosts}
}" -i etc/base.cfg
sed -re "/\[mirrors\]/ {
aallow-hosts =
a\     *localhost*
a\     *willowrise.org*
a\     *plone.org*
a\     *zope.org*
a\     *effbot.org*
a\     *python.org*
a\     *initd.org*
a\     *googlecode.com*
a\     *plope.com*
a\     *bitbucket.org*
a\     *repoze.org*
a\     *crummy.com*
a\     *minitage.org*
a\     *bpython-interpreter.org*
a\     *stompstompstomp.com*
a\     *ftp.tummy.com*
a\     *pybrary.net*
a\     *www.tummy.com*
a\     *www.riverbankcomputing.com*
a\     *.selenic.com*
}" -i etc/sys/settings.cfg
sed  -re "s/dependencies=/dependencies=git-1.7 subversion-1.6 /g" -i minilays/*/*
sed -re "s:/.env:/$PROJECT.env:g" -i etc/project/$PROJECT.cfg

cat >>  etc/project/$PROJECT.cfg << EOF

[async.test]
recipe = collective.xmltestreport
eggs = \${instance:eggs}
    plone.app.async
extra-paths = \${instance:extra-paths}
defaults = ['--exit-with-status', '--auto-color', '--auto-progress', '-s', 'plone.app.async']
environment = testenv
extra-paths = \${zopepy:extra-paths}

[cron.test]
recipe = collective.xmltestreport
eggs = \${instance:eggs}
    collective.cron
extra-paths = \${instance:extra-paths}
defaults = ['--exit-with-status', '--auto-color', '--auto-progress', '-s', 'collective.cron']
environment = testenv
extra-paths = \${zopepy:extra-paths}

EOF



# vim:set et sts=4 ts=4 tw=80:
