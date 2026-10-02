"""Restore the exact current full-text SQLite from its byte-preserving gzip delivery.

No downloads or installations. A differing existing corpus.sqlite is never replaced.
"""
import gzip,hashlib,json,os,sqlite3,tempfile
from pathlib import Path

def digest(data):
    return hashlib.sha256(data).hexdigest()

def validate_database(path,root,manifest,expected_count):
    with sqlite3.connect(path.as_uri()+'?mode=ro',uri=True) as db:
        if db.execute('PRAGMA integrity_check').fetchone()[0]!='ok':
            raise ValueError('SQLite integrity check failed')
        if db.execute('PRAGMA foreign_key_check').fetchall():
            raise ValueError('SQLite foreign-key check failed')
        rows=db.execute('SELECT problem_id,status,tex_content,tex_sha256,source_id FROM problems').fetchall()
        items={item['problem_id']:item for item in manifest['items']}
        if len(items)!=len(manifest['items']) or len(rows)!=expected_count or set(row[0] for row in rows)!=set(items):
            raise ValueError('SQLite count or unique item set mismatch')
        for identifier,status,content,tex_hash,source_id in rows:
            item=items[identifier];raw=(root/item['item_path']).read_bytes()
            if status!='verified_editable_tex' or status!=item['status'] or source_id!=item['source_id']:
                raise ValueError('SQLite status/source mismatch: '+identifier)
            if content!=raw.decode('utf8') or tex_hash!=item['tex_sha256'] or digest(raw)!=tex_hash:
                raise ValueError('SQLite full-text mismatch: '+identifier)

def restore(root):
    root=Path(root).resolve();delivery=json.loads((root/'database-delivery.json').read_text(encoding='utf8'))
    compressed=(root/'corpus.sqlite.gz').read_bytes()
    if len(compressed)!=delivery['gzip_bytes'] or digest(compressed)!=delivery['gzip_sha256']:
        raise ValueError('compressed database digest/size mismatch')
    raw=gzip.decompress(compressed)
    if len(raw)!=delivery['sqlite_bytes'] or digest(raw)!=delivery['sqlite_sha256']:
        raise ValueError('decompressed database digest/size mismatch')
    manifest_bytes=(root/'manifest.json').read_bytes()
    if digest(manifest_bytes)!=delivery['manifest_sha256']:
        raise ValueError('Current manifest digest mismatch')
    manifest=json.loads(manifest_bytes)
    destination=root/'corpus.sqlite'
    if destination.exists():
        if destination.read_bytes()!=raw:
            raise FileExistsError('Refusing to overwrite a differing existing corpus.sqlite')
        validate_database(destination,root,manifest,delivery['problem_count'])
        return destination
    fd,name=tempfile.mkstemp(prefix='.sqlite-restore-',suffix='.tmp',dir=root);temporary=Path(name)
    try:
        with os.fdopen(fd,'wb') as stream:
            stream.write(raw);stream.flush();os.fsync(stream.fileno())
        validate_database(temporary,root,manifest,delivery['problem_count'])
        os.link(temporary,destination)  # Atomic creation; fails if another file appeared.
    finally:
        temporary.unlink(missing_ok=True)
    return destination

if __name__=='__main__':
    print('Restored verified full-text SQLite:',restore(Path(__file__).resolve().parent))
