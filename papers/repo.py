from .color import colored
import os

import files
from paper import Paper


ALPHABET = 'abcdefghijklmopqrstuvwxyz'
BASE_FILE = 'papers.yaml'
BIB_DIR = 'bibdata'
META_DIR = 'meta'
DOC_DIR = 'doc'


class Repository(object):

    def __init__(self):
        self.papersdir = None
        self.citekeys = []

    # loading existing papers

    def paper_from_citekey(self, citekey):
        """Load a paper by its citekey from disk, if necessary."""
        return Paper.load(self.path_to_paper_file(citekey, 'bib'),
            metapath=self.path_to_paper_file(citekey, 'meta'))

    def citekey_from_ref(self, ref, fatal=True):
        """Tries to get citekey from given ref.
        Ref can be a citekey or a number.
        """
        if ref in self.citekeys:
            return ref
        else:
            try:
                return self.citekeys[int(ref)]
            except (IndexError, ValueError):
                if fatal:
                    print(colored('error', 'error')
                            + ': no paper with reference {}'.format(
                        colored(ref, 'citekey')))
                    exit(-1)
                raise(IOError('file not found'))

    def paper_from_ref(self, ref, fatal=True):
        key = self.citekey_from_ref(ref, fatal=fatal)
        return self.paper_from_citekey(key)

    # creating new papers

    def add_paper_from_paths(self, docpath, bibpath):
        p = Paper.load(bibpath)
        p.set_document(docpath)
        self.add_paper(p)

    def add_paper(self, p):
        if p.citekey is None:  # TODO also test if citekey is valid
            raise(ValueError("Invalid citekey: %s." % p.citekey))
        elif p.citekey in self.citekeys:
            raise(ValueError("Citekey already exists in repository: %s"
                    % p.citekey))
        self.citekeys.append(p.citekey)
        # write paper files
        self.save_paper(p)
        # update repository files
        self.save()
        # TODO change to logging system (17/12/2012)
        print "Added: %s" % p.citekey

    def add_or_update(self, paper):
        if not paper.citekey in self.citekeys:
            self.add_paper(paper)
        else:
            self.save_paper(paper)

    def save_paper(self, paper):
        if not paper.citekey in self.citekeys:
            raise(ValueError('Paper not in repository, first add it.'))
        paper.save_to_disc(self.path_to_paper_file(paper.citekey, 'bib'),
                self.path_to_paper_file(paper.citekey, 'meta'))

    def get_free_citekey(self, paper, citekey=None):
        """Create a unique citekey for the given paper.
        """
        if citekey is None:
            citekey = paper.generate_citekey()
        num = []
        while citekey + _to_suffix(num) in self.citekeys:
            _str_incr(num)
        return citekey + _to_suffix(num)

    def base_file_path(self):
        return os.path.join(self.papersdir, 'papers.yaml')

    def size(self):
        return len(self.citekeys)

    def save(self):
        papers_config = {'citekeys': self.citekeys}
        files.write_yamlfile(self.base_file_path(), papers_config)

    def load(self):
        papers_config = files.read_yamlfile(self.base_file_path())
        self.citekeys = papers_config['citekeys']

    def init(self, papersdir):
        self.papersdir = papersdir
        os.makedirs(os.path.join(self.papersdir, BIB_DIR))
        os.makedirs(os.path.join(self.papersdir, META_DIR))
        self.save()

    def path_to_paper_file(self, citekey, file_):
        if file_ == 'bib':
            return os.path.join(self.papersdir, BIB_DIR, citekey + '.bibyaml')
        elif file_ == 'meta':
            return os.path.join(self.papersdir, META_DIR, citekey + '.meta')
        else:
            raise(ValueError("%s is not a valid paper file." % file_))

    def get_document_directory(self, config):
        if config.has_option('papers', 'document-directory'):
            return config.get('papers', 'document-directory')
        else:
            return os.path.join(self.papersdir, DOC_DIR)

    def all_papers(self):
        for key in self.citekeys:
            yield self.paper_from_citekey(key)

    @classmethod
    def from_directory(cls, papersdir=None):
        repo = cls()
        if papersdir is None:
            papersdir = files.find_papersdir()
        repo.papersdir = files.clean_path(papersdir)
        repo.load()
        return repo


def _char_incr(c):
    return chr(ord(c) + 1)


def _str_incr(l):
    """Increment a number in a list string representation.

    Numbers are represented in base 26 with letters as digits.
    """
    pos = 0
    while pos < len(l):
        if l[pos] == 'z':
            l[pos] = 'a'
            pos += 1
        else:
            l[pos] = _char_incr(l[pos])
            return
    l.append('a')


def _to_suffix(l):
    return ''.join(l[::-1])
