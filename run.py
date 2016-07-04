import oursql
import datetime
import ConfigParser
from mwclient import Site
import datetime

def get_config(fname):
    config = {}
    parser = ConfigParser.SafeConfigParser()
    parser.read([fname])
    return parser


def get_results(config):
    rs = []
    db = oursql.connect(**config)
    cursor = db.cursor()
    cursor.execute("SELECT 'Ancientpages' AS TYPE, page_namespace AS namespace, page_title AS title, UNIX_TIMESTAMP(rev_timestamp) AS VALUE FROM page, revision WHERE page_namespace = 0 AND page_is_redirect = 0 AND page_latest=rev_id ORDER BY VALUE ASC LIMIT 0,2000")
    # cursor.execute("SELECT 'Ancientpages' AS TYPE, page_namespace AS namespace, page_title AS title, UNIX_TIMESTAMP(rev_timestamp) AS VALUE FROM page, revision LIMIT 0,100")
    for row in cursor:
        rs.append([row[2], row[3]])
    return rs


def output_results(results, config):
    txt = u'\n'
    for res in results:
        dt = datetime.datetime.fromtimestamp(int(res[1])).strftime('%F')
        title = res[0].decode('utf-8')
        txt += u'# [[%s]] (%s)\n' % (title, dt)

    site = Site(('https', config['host']), clients_useragent=config['clients_useragent'], **config)
    page = site.pages[config['page']]

    oldtxt = page.text()
    tagstart = u'<!--Bot:StartListe-->'
    posstart = oldtxt.find(tagstart)
    if posstart == -1:
        raise StandardError("Fant ikke tagstart")
    posstart += len(tagstart)
    
    txt = oldtxt[:posstart] + txt
    page.save(txt, config['summary'])


a = datetime.datetime.now()

for cnf in ['config.no.cnf', 'config.nn.cnf']:
    config = get_config(cnf)
    dbconf = dict(config.items('db'))
    mwconf = dict(config.items('mw'))
    output_results(get_results(dbconf), mwconf)

b = datetime.datetime.now()
c = b - a
print "Completed in %d seconds" % (c.total_seconds())

