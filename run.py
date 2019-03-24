# encoding=utf-8
import mysql.connector
import datetime
import configparser
from mwclient import Site


class MyConverter(mysql.connector.conversion.MySQLConverter):

    def row_to_python(self, row, fields):
        row = super(MyConverter, self).row_to_python(row, fields)

        def to_unicode(col):
            if type(col) == bytearray:
                return col.decode('utf-8')
            return col

        return[to_unicode(col) for col in row]


def get_config(fname):
    parser = configparser.ConfigParser()
    parser.read(fname, encoding='utf-8')
    return parser


def get_results(config, dabcat, include_dab=True):
    rs = []
    dab_crit=''
    if not include_dab:
        dab_crit = ' AND ISNULL(cl_to)'
    db = mysql.connector.connect(converter_class=MyConverter, **config)
    cursor = db.cursor()
    cursor.execute("""SELECT
      page_title AS title,
      UNIX_TIMESTAMP(rev_timestamp) AS timestamp,
      cl_to
    FROM
      revision, page
    LEFT JOIN
      categorylinks
      ON cl_from = page_id
      AND cl_to = %s
    WHERE
      page_namespace = 0
      AND page_is_redirect = 0
      AND page_latest = rev_id
      {}
    ORDER BY
      rev_timestamp ASC, title ASC
    LIMIT 0,5000""".format(dab_crit), [dabcat])
    for row in cursor:
        rs.append([row[0], row[1], row[2] is not None])
    return rs


def output_results(results, siteconf, pageconf):
    txt = u'\n'
    for res in results:
        dt = datetime.datetime.fromtimestamp(int(res[1])).strftime('%F')
        title = res[0].replace('_', ' ')
        dab = pageconf['dabdesc']
        if res[2]:
            x = u"''[[{}]]'' ({}, {})".format(title, dab, dt)
        else:
            x = u"[[{}]] ({})".format(title, dt)
        txt += u'# {}\n'.format(x)

    site = Site(**siteconf)
    pagename = pageconf['page']
    page = site.pages[pagename]
    if not page.exists:
        raise StandardError(u"Page does not exist")

    oldtxt = page.text()
    tagstart = u'<!--Bot:StartListe-->'
    posstart = oldtxt.find(tagstart)
    if posstart == -1:
        raise StandardError("Fant ikke tagstart")
    posstart += len(tagstart)

    txt = oldtxt[:posstart] + txt
    page.save(txt, pageconf['summary'])


a = datetime.datetime.now()

for cnf in ['config.no.cnf', 'config.nn.cnf']:
    print()
    print('Config: %s' % cnf)
    config = get_config(cnf)
    dbconf = dict(config.items('db'))
    mwconf = dict(config.items('site'))
    for p in ['page2', 'page']:
        pageconf = dict(config.items(p))
        print((('Page: %s' % pageconf['page']).encode('utf-8')))
        catname = pageconf['dabcat']
        include_dab = pageconf['include_dab'].lower()[0] == 't'
        output_results(get_results(dbconf, catname, include_dab), mwconf, pageconf)

b = datetime.datetime.now()
c = b - a
print("Completed in %d seconds" % c.total_seconds())
