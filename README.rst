==============================================================
BUILDOUT FOR libertic.event DOCUMENTATION
==============================================================

INSTALLING THIS PROJECT WITHOUT MINITAGE
-----------------------------------------
::

    git clone ssh://git@github.com/LiberTIC/libertic.event.buildout.git -b master|prod|preprod libertic.event
    cd libertic.event
    python bootstrap.py -dc buildout-(dev/prod).cfg
    bin/buildout -vvvvvNc -dc buildout-(dev/prod).cfg

INSTALLING THIS PROJECT VITH MINITAGE
--------------------------------------
ALWAYS USE THE MINITAGE ENVIRONMENT FILE INSIDE A MINITAGE
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Before doing anything in your project just after being installed, just source the environment file in your current shell::

    source $MT/zope/libertic.event/sys/share/minitage/minitage.env # env file is generated with $MT/bin/paster create -t minitage.instances.env libertic.event

THE MINITAGE DANCE
~~~~~~~~~~~~~~~~~~~~~~~~
::

    export MT=/minitage
    mkdir $MT -pv $MT/zope $MT/minilays
    cd $MT
    wget -O minitagetool.sh https://raw.github.com/minitage/minitage.shell/master/minitagetool.sh
    git clone ssh://git@github.com/LiberTIC/libertic.event.buildout.git $MT/zope/libertic.event
    # or git clone ssh://git@github.com/LiberTIC/libertic.event.buildout.git -b prod $MT/zope/libertic.event-prod
    # or git clone ssh://git@github.com/LiberTIC/libertic.event.buildout.git -b preprod $MT/zope/libertic.event-preprod
    ln -sfv MT/zope/libertic.event*/*minilay $MT/minilays/libertic
    $MT/minitagetool.sh bootstrap libertic.event
    # or $MT/minitagetool.sh bootstrap libertic.event-prod
    # or $MT/minitagetool.sh bootstrap libertic.event-preprod

PRODUCTION MODE
---------------
To make your application safe for production, run the ``(minitage.)buildout-prod.cfg`` buildout'.
It extends this one with additionnal crontabs and backup scripts and some additionnal instances creation.

In production we use supervisor to manage processes.

Those processes are managed via supervisor (the only init script you add to your system init):

    - zeo
    - haproxy (loadbalancer)
    - instance1 (plone)
    - instance-worker (asynchron jobs runner)

We also add crons to backup & pack the ZODB each night


BASE BUILDOUTS WHICH DO ONLY SCHEDULE PARTS FROM THERE & THERE
-------------------------------------------------------------------
Love to know that Minitage support includes xml libs, ldap, dbs; python, dependencies & common eggs cache for things like lxml or Pillow), subversion & much more.
::

    |-- etc/base.cfg               -> The base buildout
    |-- buildout-prod.cfg          -> buildout for production
    |-- buildout-dev.cfg           -> buildout for development
    |-- etc/minitage/minitage.cfg  -> some buildout tweaks to run in the best of the world with minitage
    |-- minitage.buildout-prod.cfg -> buildout for production  with minitage support
    |-- minitage.buildout-dev.cfg  -> buildout for development with minitage support


PLONE OFFICIAL BUILDOUTS INTEGRATION
--------------------------------------
In ``etc/base.cfg``, we extends directly plone release versions & sources files.


PROJECT SETTINGS
~~~~~~~~~~~~~~~~~~~~~~~~
- Think you have the most important sections of this buildout configuration in etc/libertic.event.cfg
Set the project developement  specific settings there
::

    etc/project/
    |-- libertic.event.cfg       -> your project needs (packages, sources, products)
    |-- sources.cfg          -> externals sources of your project:
    |                           - Sources not packaged as python eggs.
    |                           - Eggs Grabbed from svn, add here your develoment eggs.
    |                           - Links to find distributions.
    |-- patches.cfg          -> patches used on the project
    |-- cluster.cfg          -> define new zope instances here & also their FileSystemStorage if any.
    |-- libertic.event-kgs.cfg   -> Generated KGS for your project (minitage's printer or buildout.dumppickledversion)
    `-- versions.cfg         -> minimal version pinning for installing your project


SYSTEM ADMINISTRATORS RELATED FILES
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
::

    etc/init.d/                 -> various init script (eg supervisor)
    etc/logrotate.d/            -> various logrotate configuration files
    etc/sys/
    |-- high-availability.cfg   -> Project production settings like supervision, loadbalancer and so on
    |-- maintenance.cfg         -> Project maintenance settings (crons, logs)
    `-- settings.cfg            -> various settings (crons hours, hosts, installation paths, ports, passwords)


REVERSE PROXY
--------------
We generate two virtualhosts for a cliassical apache setup, mostly ready but feel free to copy/adapt.
::
    etc/apache/
    |-- 100-libertic.event.reverseproxy.conf     -> a vhost for ruse with a standalone plone (even with haproxy in front of.)
    `-- apache.cfg
    etc/templates/apache/
    |-- 100-libertic.event.reverseproxy.conf.in  -> Template for a vhost for ruse with a standalone plone (even with haproxy in front of.)

In settings.cfg you have now some settings for declaring which host is your reverse proxy backend & the vhost mounting:
    * hosts:zope-front / ports:zope-front                              -> zope front backend
    * reverseproxy:host / reverseproxy:port / reverseproxy:mount-point -> host / port / mountpoint on the reverse proxy)

CONFIGURATION TEMPLATES
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
::

    etc/templates/
    |-- balancer.conf.template      -> haproxy template.
    |                                  Copy or ln the generated file 'etc/loadbalancing/balancer.conf' to your haproxy installation if any.
    `-- logrotate.conf.template     -> logrotate configuration file template for your Zope logs
    `-- supervisor.initd            -> template for supervisor init script


.. vim:set ft=rst:
