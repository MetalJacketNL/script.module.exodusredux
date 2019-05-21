import hashlib

from resources.lib.modules import control

try:
    from sqlite3 import dbapi2 as database
except Exception:
    from pysqlite2 import dbapi2 as database

class Bookmark:
    def __init__(self, offset):
        self.offset = offset

def get(name, year='0'):

    try:
        bookmark = Bookmark(0)
        if not control.setting('bookmarks') == 'true':
            raise Exception()

        name = name.replace(" ", "").lower()

        idFile = generate_file_id(name, year)
        dbcon = database.connect(control.bookmarksFile)
        dbcur = dbcon.cursor()
        dbcur.execute("SELECT * FROM bookmark WHERE idFile = '%s'" % idFile)
        match = dbcur.fetchone()

        offset = float(match[1])

        bookmark.offset = offset

        dbcon.close()

        if bookmark.offset == 0.0:
            raise Exception()

        minutes, seconds = divmod(float(bookmark.offset), 60)
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
    except:
        return bookmark


def insert(name, progressPercentage, year='0'):
    try:
        if not control.setting('bookmarks') == 'true':
            raise Exception()

        ok = int(progressPercentage) >= 2 and progressPercentage <= 92
        name = name.replace(" ", "").lower()
        idFile = generate_file_id(name, year)

        control.makeFile(control.dataPath)
        dbcon = database.connect(control.bookmarksFile)
        dbcur = dbcon.cursor()
        dbcur.execute(
            "CREATE TABLE IF NOT EXISTS bookmark ("
            "idFile TEXT, "
            "timeInPercentage TEXT,"
            "UNIQUE(idFile)"
            ");")
        dbcur.execute("DELETE FROM bookmark WHERE idFile = '%s'" % idFile)
        if ok:
            dbcur.execute("INSERT INTO bookmark Values (?, ?)", (idFile, progressPercentage))
        dbcon.commit()
        dbcon.close()
    except Exception:
        pass

def generate_file_id(name, year):
    idFile = hashlib.md5()
    for i in name:
        idFile.update(str(i))
    for i in year:
        idFile.update(str(i))
    idFile = str(idFile.hexdigest())

    return idFile