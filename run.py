import oursql
import datetime
import ConfigParser
from mwclient import Site


def get_config(fname):
    parser = ConfigParser.SafeConfigParser()
    parser.read([fname])
    return parser


def get_results(config, dabcat):
    rs = []
    db = oursql.connect(**config)
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
      AND cl_to = ?
    WHERE
      page_namespace = 0
      AND page_is_redirect = 0
      AND page_latest = rev_id
    ORDER BY
      rev_timestamp ASC
    LIMIT 0,2000""", (dabcat,))
    for row in cursor:
        rs.append([row[0], row[1], row[2] is not None])
    return rs


def output_results(results, config):
    txt = u'\n'
    for res in results:
        dt = datetime.datetime.fromtimestamp(int(res[1])).strftime('%F')
        title = res[0].decode('utf-8').replace('_', ' ')
        dab = config['dabdesc'].decode('utf-8')
        if res[2]:
            x = u"''[[{}]]'' ({}, {})".format(title, dab, dt)
        else:
            x = u"[[{}]] ({})".format(title, dt)
        txt += u'# {}\n'.format(x)

    site = Site(('https', config['host']), clients_useragent=config['clients_useragent'])
    site.login(config['user'], config['passwd'])
    pagename = config['page'].decode('utf-8')
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
    page.save(txt, config['summary'].decode('utf-8'))


a = datetime.datetime.now()

for cnf in ['config.no.cnf', 'config.nn.cnf']:
    print 'Using: {}'.format(cnf)
    config = get_config(cnf)
    dbconf = dict(config.items('db'))
    mwconf = dict(config.items('mw'))
    output_results(get_results(dbconf, mwconf['dabcat'].decode('utf-8')), mwconf)

b = datetime.datetime.now()
c = b - a
print "Completed in %d seconds" % (c.total_seconds())
