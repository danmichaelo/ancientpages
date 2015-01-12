**ancientpages**

Rewrite of an ol' tool by Laaknor for use with Tool Labs.

Generates
https://no.wikipedia.org/wiki/Wikipedia:Gamle_sider

Setup:

    virtualenv ENV
    . ENV/bin/activate
    pip install oursql mwclient

Crontab:

    MAILTO=""
    49 3 * * * cd ancientpages && jsub -once -j y -cwd -N ancientpages -mem 368m -o ancientpages.log run.sh

