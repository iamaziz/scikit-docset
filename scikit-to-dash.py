import requests
import sqlite3
import os
import urllib
from bs4 import BeautifulSoup as bs


def main():
    # download html documentation
    cmdcommand = """ cd . && rm -rf Scikit.docset && mkdir -p Scikit.docset/Contents/Resources/Documents && cd Scikit.docset && httrack -%v2 -T60 -R99 --sockets=7 -%c1000 -c10 -A999999999 -%N0 --disable-security-limits -F 'Mozilla/5.0 (X11; Linux i686) AppleWebKit/535.19 (KHTML, like Gecko) Ubuntu/11.10 Chromium/18.0.1025.168' --mirror --keep-alive --robots=0 "http://scikit-learn.org/stable/" -n -* +*.css +*css.php +*.ico +*/fonts/* +*.svg +*.ttf +fonts.googleapis.com* +*.woff +*.eot +*.png +*.jpg +*.gif +*.jpeg +*.js +http://scikit-learn.org/stable/* -github.com* +raw.github.com* && rm -rf hts-* && mkdir -p Contents/Resources/Documents && mv -f *.* Contents/Resources/Documents/ """
    os.system(cmdcommand)

    # docset config
    docset_name = 'Scikit-learn.docset'
    output = docset_name + '/Contents/Resources/Documents/'

    # create docset directory
    if not os.path.exists(output):
        os.makedirs(output)

    # add icon
    icon = 'http://nbviewer.ipython.org/github/glouppe/talk-sklearn-mloss-nips2013/blob/master/oral/sklearn-logo.png'
    urllib.urlretrieve(icon, docset_name + "/icon.png")

    return docset_name


def update_db(name, typ, path):
    try:
        cur.execute("SELECT rowid FROM searchIndex WHERE path = ?", (path,))
        dbpath = cur.fetchone()
        cur.execute("SELECT rowid FROM searchIndex WHERE name = ?", (name,))
        dbname = cur.fetchone()

        if dbpath is None and dbname is None:
            cur.execute('INSERT OR IGNORE INTO searchIndex(name, type, path) VALUES (?,?,?)', (name, typ, path))
            print(
                'DB add >> name: {0} | type: {1} | path: {2}'.format(name, typ, path))
        else:
            print("record exists")

    except:
        pass


def add_urls():
    # index pages
    pages = {'Sample':'http://scikit-learn.org/stable/auto_examples/index.html',
             'Class':'http://scikit-learn.org/stable/modules/classes.html',
             'Guide':'http://scikit-learn.org/stable/user_guide.html',
             'Resource':'http://scikit-learn.org/stable/tutorial/basic/tutorial.html', }

    filtered = ('http', '/')
    dir_path = ['Class', 'Sample', 'Guide']
    in_page = ['Resource']

    # loop through index pages:
    for p in pages:
        typ = p

        # soup each index page
        html = requests.get(pages[typ]).text
        soup = bs(html)

        for a in soup.findAll('a'):
            name = a.text.strip()
            href = a.get('href')
            name = name.replace('\n', '')

            base_path = pages[typ].replace('http://', '')

            if href is not None and len(href) > 1 and len(name) > 2 and not href.startswith(filtered):
                if typ in dir_path:
                    if not href.startswith('#'):
                        base_path = base_path.replace(base_path.split('/')[-1], '')
                    path = base_path + href
                    # Populate the SQLite Index
                    update_db(name, typ, path)
                elif typ in in_page and href.startswith('#'):
                    path = base_path + href
                    # Populate the SQLite Index
                    update_db(name, typ, path)


def add_infoplist():
    name = docset_name.split('.')[0]
    info = " <?xml version=\"1.0\" encoding=\"UTF-8\"?>"\
           "<!DOCTYPE plist PUBLIC \"-//Apple//DTD PLIST 1.0//EN\" \"http://www.apple.com/DTDs/PropertyList-1.0.dtd\"> "\
           "<plist version=\"1.0\"> "\
           "<dict> "\
           "    <key>CFBundleIdentifier</key> "\
           "    <string>{0}</string> "\
           "    <key>CFBundleName</key> "\
           "    <string>{1}</string>"\
           "    <key>DocSetPlatformFamily</key>"\
           "    <string>{2}</string>"\
           "    <key>isDashDocset</key>"\
           "    <true/>"\
           "    <key>isJavaScriptEnabled</key>"\
           "    <true/>"\
           "    <key>dashIndexFilePath</key>"\
           "    <string>{3}</string>"\
           "</dict>"\
           "</plist>".format(name, name, name, 'scikit-learn.org/stable/' + 'index.html')

    open(docset_name + '/Contents/info.plist', 'wb').write(info)


if __name__ == '__main__':
    # download html and create docset folder
    docset_name = main()

    # create and connect to SQLite db
    db = sqlite3.connect(docset_name + '/Contents/Resources/docSet.dsidx')
    cur = db.cursor()
    try:
        cur.execute('DROP TABLE searchIndex;')
    except:
        pass
        cur.execute('CREATE TABLE searchIndex(id INTEGER PRIMARY KEY, name TEXT, type TEXT, path TEXT);')
        cur.execute('CREATE UNIQUE INDEX anchor ON searchIndex (name, type, path);')

    # scan index pages and populate SQLite
    add_urls()
    add_infoplist()

    # commit and close db
    db.commit()
    db.close()
