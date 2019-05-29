import hashlib, json, xbmc

from resources.lib.modules import control

try:
    from sqlite3 import dbapi2 as database
except Exception:
    from pysqlite2 import dbapi2 as database


class Bookmark:
    def __init__(self, offset = 0, meta = '', content_type = ''):
        self.offset = offset
        self.meta = meta
        self.content_type = content_type


def get(name, year='0'):
    try:
        bookmark = Bookmark()
        if not control.setting('bookmarks') == 'true':
            raise Exception()

        name = name.replace(" ", "").lower()

        idFile = generate_file_id(name, year)
        
        dbcon = database.connect(control.bookmarksFile)
        dbcur = dbcon.cursor()
        dbcur.execute("SELECT * FROM bookmark WHERE idFile = '%s'" % idFile)
        match = dbcur.fetchone()

        if match is not None:
            offset = float(match[1])
            meta = json.loads(match[2])
            content_type = str(match[3])
            bookmark = Bookmark(offset or 0.0, meta, content_type)

        dbcon.close()

        if bookmark.offset == 0.0:
            raise Exception()

        offset_label = float(bookmark.meta['duration']) * (bookmark.offset / 100)

        minutes, seconds = divmod(float(offset_label), 60)
        hours, minutes = divmod(minutes, 60)
        label = '%02d:%02d:%02d' % (hours, minutes, seconds)
        label = (control.lang(32502) % label).encode('utf-8')

        try:
            yes = control.dialog.contextmenu([label, control.lang(32501).encode('utf-8'), ])
        except Exception:
            yes = control.yesnoDialog(
                label, '', '', str(name),
                control.lang(32503).encode('utf-8'),
                control.lang(32501).encode('utf-8'))

        if yes:
            bookmark.offset = 0.0

        return bookmark
    except Exception as e:
        return bookmark


def insert(name, progress_percentage, meta, content_type):
    try:
        if not control.setting('bookmarks') == 'true':
            raise Exception()

        ok = int(progress_percentage) >= 2 and progress_percentage <= 92
        name = name.replace(" ", "").lower()
        idFile = generate_file_id(name, meta['year'])

        control.makeFile(control.dataPath)
        dbcon = database.connect(control.bookmarksFile)
        dbcur = dbcon.cursor()
        dbcur.execute(
            "CREATE TABLE IF NOT EXISTS bookmark ("
            "idFile TEXT, "
            "timeInPercentage TEXT,"
            "meta TEXT,"
            "contentType TEXT,"
            "UNIQUE(idFile)"
            ");")
        dbcur.execute("DELETE FROM bookmark WHERE idFile = '%s'" % idFile)
        if ok:
            dbcur.execute("INSERT INTO bookmark Values (?, ?, ?, ?)", (idFile, progress_percentage, json.dumps(meta), content_type))

        dbcon.commit()
        dbcon.close()
    except Exception as e:
        xbmc.log(str(e))
        pass

def generate_file_id(name, year):
    idFile = hashlib.md5()
    for i in name:
        idFile.update(str(i))
    for i in year:
        idFile.update(str(i))
    idFile = str(idFile.hexdigest())

    return idFile