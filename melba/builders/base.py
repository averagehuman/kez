
import os
from os.path import join as pathjoin, exists as pathexists, dirname, abspath, basename
from cStringIO import StringIO
import mimetypes
import tempfile
import shutil
from datetime import datetime
from fnmatch import fnmatch

from django.conf import settings
from django.template.defaultfilters import slugify
from django.core import management

from simples3 import S3Bucket
from gravy import anyrepo

from bigmouth import models as bigmouth
from bigmouth.yuitoc import write_yuitoc

RESULTS = dict((y, x) for (x, y) in bigmouth.BuildRecord.FLAGS)

buildersdir = dirname(abspath(__file__))
builtin_theme_dir = pathjoin(dirname(buildersdir), 'themes')

class DochoundBuildException(Exception):
    pass

class BuilderBase(object):
    DOCTYPE = None

    def __init__(self, doc):
        #if self.DOCTYPE:
        #    doc = getattr(doc, self.DOCTYPE.lower() + 'document')
        self.doc = doc
        outdir = doc.get_storage_root()
        if not pathexists(outdir):
            os.makedirs(outdir)
        self.outdir = outdir
        slug = doc.url_slug or 'sources'
        self.srcdir = pathjoin(
            tempfile.mkdtemp(prefix='bigmouth-', suffix='-'+slug),
            slug,
        )
        self.apidir = pathjoin(self.srcdir, '_api')
        self.logfile = pathjoin(self.outdir, 'bigmouth.log')
        self.note = lambda s: self._log.write(s+'\n')
        self.record = None
        self._log = None
        self._repo = None

    @property
    def repo(self):
        if self._repo is None:
            branch = self.doc.branch
            repo = branch.repo
            repo = anyrepo(repo.owner.provider, repo.owner.username, repo.slug)
            repo.clone()
            try:
                repo.pull(update=True)
            except:
                pass
            repo.checkout(branch.name)
            self._repo = repo
        return self._repo

    def set_result(self, label, message=None):
        self.record.status = RESULTS[label]
        self.record.status_msg = message or ''

    # unused
    def get_document_context(self):
        return {
            'doc_slug': self.doc.url_slug,
        }

    def get_sources(self, globs=None, dest_format=None, markup_flavor=None):
        assert not pathexists(self.srcdir)
        docroot = self.doc.docroot
        docfile = self.doc.docfile
        if docfile:
            src = pathjoin(docroot, docfile)
            dest = pathjoin(self.srcdir, docfile)
            self.repo.copyfile(src, dest)
        else:
            self.repo.copyfiles(self.srcdir, root=docroot, symlinks=True)

    def write_toc(self, master_doc, nodes):
        outfile = self.doc.get_storage_root() + 'toc.js'
        write_yuitoc(outfile, master_doc, self.doc.get_storage_url(), nodes)

    def build(self, **kw):
        raise NotImplementedError()

    def build_python_api(self, package_name=None, package_root=None):
        package_root = package_root or ''
        package_root = package_root.strip('/')
        doc = self.doc
        kwargs = dict(
            branch=doc.branch,
            doctype='EPYDOC',
            category=doc.category,
        )
        if package_name and package_root:
            pyfiles = [(package_name, package_root)]
        else:
            #find packages and modules
            manifest = self.repo.find_py_files()
            #ignore modules if there are packages
            pyfiles = manifest['packages'] or manifest['modules']
            found = set(X[1] for X in pyfiles)
            for obj in bigmouth.EpydocDocument.objects.filter(**kwargs):
                if obj.docroot not in found:
                    obj.delete()
        for name, path in pyfiles:
            query = dict(kwargs)
            if path.endswith('.py'):
                query['docfile'] = basename(path)
                query['module'] = name
                path = dirname(path)
            query['docroot'] = path
            document, new = bigmouth.EpydocDocument.objects.get_or_create(**query)
            if new:
                try:
                    title = "%s %s python API (%s)" % (doc.repo_slug, doc.branch.name, path)
                    document.title = title[:100]
                    document.url_slug = slugify(title.replace('python', 'py').replace('/', ' '))
                    document.package_name = name[:80]
                    document.hidden = True
                    document.save()
                    doc.associated.add(document)
                except Exception, e:
                    try:
                        document.delete()
                    except:
                        pass
                    raise Exception("Error while creating new Epydoc document - %s" % e)
            document.build()

    def start(self):
        self._log = open(self.logfile, 'wb')
        record = bigmouth.BuildRecord(document=self.doc, start=datetime.now())
        record.save()
        self.record = record

    def finish(self, **kw):
        try:
            stores = [s.strip().lower() for s in kw.get('store', '').split(',')]
            for store in stores:
                if store:
                    store_method = getattr(self, 'store_' + store)
                    store_method(**kw)
            clean = kw.get('clean', False)
            if clean:
                # remove the local store
                if pathexists(self.outdir):
                    shutil.rmtree(self.outdir)
            if pathexists(self.srcdir):
                shutil.rmtree(self.srcdir)
        except Exception, e:
            self.set_result('ERROR', str(e))
        else:
            self.set_result('SUCCESS')
        finally:
            try:
                self.record.finish = datetime.now()
                self.record.save()
            except:
                pass
            try:
                self._log.close()
            except:
                pass


    def store_all(self, **kw):
        self.store_s3(**kw)

    def store_none(self, **kw):
        pass

    def store_s3(self, **kw):
        s3_bucket = kw.get(
            's3_bucket',
            getattr(settings, 'DOCHOUND_S3_BUCKET_NAME', None),
        )
        if not s3_bucket:
            raise DochoundBuildException("missing option 's3_bucket' or setting 'DOCHOUND_S3_BUCKET_NAME'")
        aws_access_key = kw.get(
            'aws_access_key',
            getattr(settings, 'AWS_ACCESS_KEY_ID', None),
        )
        aws_secret_key = kw.get(
            'aws_secret_key',
            getattr(settings, 'AWS_SECRET_ACCESS_KEY', None),
        )
        if not (aws_access_key and aws_secret_key):
            raise DochoundBuildException('missing AWS credentials')
        self._store_s3(
            s3_bucket,
            access_key=aws_access_key,
            secret_key=aws_secret_key
        )

    def _store_s3(self, bucketname, access_key, secret_key):
        bucket = S3Bucket(
            bucketname,
            access_key=access_key,
            secret_key=secret_key,
        )
        bucket.put_bucket(acl='public-read')
        root_url = self.doc.get_storage_key().lstrip('/')
        try:
            stored = set(t[0] for t in bucket.listdir(root_url))
        except:
            stored = set()
        for root, dirs, files in os.walk(self.outdir):
            dirs[:] = [d for d in dirs if d != '.doctrees']
            root = root.rstrip('/')
            relpath = root[len(self.outdir):]
            if relpath:
                relpath += '/'
            for f in files:
                src = root + '/' + f
                mimetype, encoding = mimetypes.guess_type(f)
                dest = root_url + relpath + f
                with open(src) as srcfile:
                    self.note('S3 PUT: %s' % dest)
                    bucket.put(dest, srcfile.read(), mimetype=mimetype, acl='public-read')
                try:
                    stored.remove(dest)
                except KeyError:
                    pass
        # remove everything from bucket that we haven't just uploaded
        for key in stored:
            self.note('S3 DELETE: %s' % key)
            bucket.delete(key)

