from nose.tools import eq_ as eq
from gitosis.test.util import assert_raises, readFile

import logging
import os
import subprocess
from cStringIO import StringIO
from ConfigParser import RawConfigParser

from gitosis import dcontrol
from gitosis import repository
from gitosis import buildhook

from gitosis.test import util

def test_bad_newLine():
    cfg = RawConfigParser()
    e = assert_raises(
        dcontrol.CommandMayNotContainNewlineError,
        dcontrol.serve,
        cfg=cfg,
        user='jdoe',
        command='ev\nil',
        )
    eq(str(e), 'Command may not contain newline')
    assert isinstance(e, dcontrol.ServingError)

def test_bad_dash_noargs():
    cfg = RawConfigParser()
    e = assert_raises(
        dcontrol.UnknownCommandError,
        dcontrol.serve,
        cfg=cfg,
        user='jdoe',
        command='git-upload-pack',
        )
    eq(str(e), 'Unknown command denied')
    assert isinstance(e, dcontrol.ServingError)

def test_bad_space_noargs():
    cfg = RawConfigParser()
    e = assert_raises(
        dcontrol.UnknownCommandError,
        dcontrol.serve,
        cfg=cfg,
        user='jdoe',
        command='git upload-pack',
        )
    eq(str(e), 'Unknown command denied')
    assert isinstance(e, dcontrol.ServingError)

def test_bad_command():
    cfg = RawConfigParser()
    e = assert_raises(
        dcontrol.UnknownCommandError,
        dcontrol.serve,
        cfg=cfg,
        user='jdoe',
        command="evil 'foo'",
        )
    eq(str(e), 'Unknown command denied')
    assert isinstance(e, dcontrol.ServingError)

def test_bad_unsafeArguments_notQuoted():
    cfg = RawConfigParser()
    e = assert_raises(
        dcontrol.UnsafeArgumentsError,
        dcontrol.serve,
        cfg=cfg,
        user='jdoe',
        command="git-upload-pack foo",
        )
    eq(str(e), 'Arguments to command look dangerous')
    assert isinstance(e, dcontrol.ServingError)

def test_bad_unsafeArguments_badCharacters():
    cfg = RawConfigParser()
    e = assert_raises(
        dcontrol.UnsafeArgumentsError,
        dcontrol.serve,
        cfg=cfg,
        user='jdoe',
        command="git-upload-pack 'ev!l'",
        )
    eq(str(e), 'Arguments to command look dangerous')
    assert isinstance(e, dcontrol.ServingError)

def test_bad_unsafeArguments_dotdot():
    cfg = RawConfigParser()
    e = assert_raises(
        dcontrol.UnsafeArgumentsError,
        dcontrol.serve,
        cfg=cfg,
        user='jdoe',
        command="git-upload-pack 'something/../evil'",
        )
    eq(str(e), 'Arguments to command look dangerous')
    assert isinstance(e, dcontrol.ServingError)

def test_bad_forbiddenCommand_read_dash():
    cfg = RawConfigParser()
    e = assert_raises(
        dcontrol.ReadAccessDenied,
        dcontrol.serve,
        cfg=cfg,
        user='jdoe',
        command="git-upload-pack 'foo'",
        )
    eq(str(e), 'Repository read access denied')
    assert isinstance(e, dcontrol.AccessDenied)
    assert isinstance(e, dcontrol.ServingError)

def test_bad_forbiddenCommand_read_space():
    cfg = RawConfigParser()
    e = assert_raises(
        dcontrol.ReadAccessDenied,
        dcontrol.serve,
        cfg=cfg,
        user='jdoe',
        command="git upload-pack 'foo'",
        )
    eq(str(e), 'Repository read access denied')
    assert isinstance(e, dcontrol.AccessDenied)
    assert isinstance(e, dcontrol.ServingError)

def test_bad_forbiddenCommand_write_noAccess_dash():
    cfg = RawConfigParser()
    e = assert_raises(
        dcontrol.ReadAccessDenied,
        dcontrol.serve,
        cfg=cfg,
        user='jdoe',
        command="git-receive-pack 'foo'",
        )
    # error message talks about read in an effort to make it more
    # obvious that jdoe doesn't have *even* read access
    eq(str(e), 'Repository read access denied')
    assert isinstance(e, dcontrol.AccessDenied)
    assert isinstance(e, dcontrol.ServingError)

def test_bad_forbiddenCommand_write_noAccess_space():
    cfg = RawConfigParser()
    e = assert_raises(
        dcontrol.ReadAccessDenied,
        dcontrol.serve,
        cfg=cfg,
        user='jdoe',
        command="git receive-pack 'foo'",
        )
    # error message talks about read in an effort to make it more
    # obvious that jdoe doesn't have *even* read access
    eq(str(e), 'Repository read access denied')
    assert isinstance(e, dcontrol.AccessDenied)
    assert isinstance(e, dcontrol.ServingError)

def test_bad_forbiddenCommand_write_readAccess_dash():
    cfg = RawConfigParser()
    cfg.add_section('group foo')
    cfg.set('group foo', 'members', 'jdoe')
    cfg.set('group foo', 'readonly', 'foo')
    e = assert_raises(
        dcontrol.WriteAccessDenied,
        dcontrol.serve,
        cfg=cfg,
        user='jdoe',
        command="git-receive-pack 'foo'",
        )
    eq(str(e), 'Repository write access denied')
    assert isinstance(e, dcontrol.AccessDenied)
    assert isinstance(e, dcontrol.ServingError)

def test_bad_forbiddenCommand_write_readAccess_space():
    cfg = RawConfigParser()
    cfg.add_section('group foo')
    cfg.set('group foo', 'members', 'jdoe')
    cfg.set('group foo', 'readonly', 'foo')
    e = assert_raises(
        dcontrol.WriteAccessDenied,
        dcontrol.serve,
        cfg=cfg,
        user='jdoe',
        command="git receive-pack 'foo'",
        )
    eq(str(e), 'Repository write access denied')
    assert isinstance(e, dcontrol.AccessDenied)
    assert isinstance(e, dcontrol.ServingError)

def test_simple_read_dash():
    tmp = util.maketemp()
    repository.init(os.path.join(tmp, 'foo.git'))
    cfg = RawConfigParser()
    cfg.add_section('gitosis')
    cfg.set('gitosis', 'repositories', tmp)
    cfg.add_section('group foo')
    cfg.set('group foo', 'members', 'jdoe')
    cfg.set('group foo', 'readonly', 'foo')
    got = dcontrol.serve(
        cfg=cfg,
        user='jdoe',
        command="git-upload-pack 'foo'",
        )
    eq(got, "git-upload-pack '%s/foo.git'" % tmp)

def test_simple_read_space():
    tmp = util.maketemp()
    repository.init(os.path.join(tmp, 'foo.git'))
    cfg = RawConfigParser()
    cfg.add_section('gitosis')
    cfg.set('gitosis', 'repositories', tmp)
    cfg.add_section('group foo')
    cfg.set('group foo', 'members', 'jdoe')
    cfg.set('group foo', 'readonly', 'foo')
    got = dcontrol.serve(
        cfg=cfg,
        user='jdoe',
        command="git upload-pack 'foo'",
        )
    eq(got, "git upload-pack '%s/foo.git'" % tmp)

def test_simple_write_dash():
    tmp = util.maketemp()
    repository.init(os.path.join(tmp, 'foo.git'))
    cfg = RawConfigParser()
    cfg.add_section('gitosis')
    cfg.set('gitosis', 'repositories', tmp)
    cfg.add_section('group foo')
    cfg.set('group foo', 'members', 'jdoe')
    cfg.set('group foo', 'writable', 'foo')
    got = dcontrol.serve(
        cfg=cfg,
        user='jdoe',
        command="git-receive-pack 'foo'",
        )
    eq(got, "git-receive-pack '%s/foo.git'" % tmp)

def test_simple_write_space():
    tmp = util.maketemp()
    repository.init(os.path.join(tmp, 'foo.git'))
    cfg = RawConfigParser()
    cfg.add_section('gitosis')
    cfg.set('gitosis', 'repositories', tmp)
    cfg.add_section('group foo')
    cfg.set('group foo', 'members', 'jdoe')
    cfg.set('group foo', 'writable', 'foo')
    got = dcontrol.serve(
        cfg=cfg,
        user='jdoe',
        command="git receive-pack 'foo'",
        )
    eq(got, "git receive-pack '%s/foo.git'" % tmp)

def test_push_inits_if_needed():
    # a push to a non-existent repository (but where config authorizes
    # you to do that) will create the repository on the fly
    tmp = util.maketemp()
    cfg = RawConfigParser()
    cfg.add_section('gitosis')
    repositories = os.path.join(tmp, 'repositories')
    os.mkdir(repositories)
    cfg.set('gitosis', 'repositories', repositories)
    generated = os.path.join(tmp, 'generated')
    os.mkdir(generated)
    cfg.set('gitosis', 'generate-files-in', generated)
    cfg.add_section('group foo')
    cfg.set('group foo', 'members', 'jdoe')
    cfg.set('group foo', 'writable', 'foo')
    dcontrol.serve(
        cfg=cfg,
        user='jdoe',
        command="git-receive-pack 'foo'",
        )
    eq(os.listdir(repositories), ['foo.git'])
    assert os.path.isfile(os.path.join(repositories, 'foo.git', 'HEAD'))

def test_push_inits_if_needed_haveExtension():
    # a push to a non-existent repository (but where config authorizes
    # you to do that) will create the repository on the fly
    tmp = util.maketemp()
    cfg = RawConfigParser()
    cfg.add_section('gitosis')
    repositories = os.path.join(tmp, 'repositories')
    os.mkdir(repositories)
    cfg.set('gitosis', 'repositories', repositories)
    generated = os.path.join(tmp, 'generated')
    os.mkdir(generated)
    cfg.set('gitosis', 'generate-files-in', generated)
    cfg.add_section('group foo')
    cfg.set('group foo', 'members', 'jdoe')
    cfg.set('group foo', 'writable', 'foo')
    dcontrol.serve(
        cfg=cfg,
        user='jdoe',
        command="git-receive-pack 'foo.git'",
        )
    eq(os.listdir(repositories), ['foo.git'])
    assert os.path.isfile(os.path.join(repositories, 'foo.git', 'HEAD'))

def test_push_inits_subdir_parent_missing():
    tmp = util.maketemp()
    cfg = RawConfigParser()
    cfg.add_section('gitosis')
    repositories = os.path.join(tmp, 'repositories')
    os.mkdir(repositories)
    cfg.set('gitosis', 'repositories', repositories)
    generated = os.path.join(tmp, 'generated')
    os.mkdir(generated)
    cfg.set('gitosis', 'generate-files-in', generated)
    cfg.add_section('group foo')
    cfg.set('group foo', 'members', 'jdoe')
    cfg.set('group foo', 'writable', 'foo/bar')
    dcontrol.serve(
        cfg=cfg,
        user='jdoe',
        command="git-receive-pack 'foo/bar.git'",
        )
    eq(os.listdir(repositories), ['foo'])
    foo = os.path.join(repositories, 'foo')
    util.check_mode(foo, 0750, is_dir=True)
    eq(os.listdir(foo), ['bar.git'])
    assert os.path.isfile(os.path.join(repositories, 'foo', 'bar.git', 'HEAD'))

def test_push_inits_subdir_parent_exists():
    tmp = util.maketemp()
    cfg = RawConfigParser()
    cfg.add_section('gitosis')
    repositories = os.path.join(tmp, 'repositories')
    os.mkdir(repositories)
    foo = os.path.join(repositories, 'foo')
    # silly mode on purpose; not to be touched
    os.mkdir(foo, 0751)
    cfg.set('gitosis', 'repositories', repositories)
    generated = os.path.join(tmp, 'generated')
    os.mkdir(generated)
    cfg.set('gitosis', 'generate-files-in', generated)
    cfg.add_section('group foo')
    cfg.set('group foo', 'members', 'jdoe')
    cfg.set('group foo', 'writable', 'foo/bar')
    dcontrol.serve(
        cfg=cfg,
        user='jdoe',
        command="git-receive-pack 'foo/bar.git'",
        )
    eq(os.listdir(repositories), ['foo'])
    util.check_mode(foo, 0751, is_dir=True)
    eq(os.listdir(foo), ['bar.git'])
    assert os.path.isfile(os.path.join(repositories, 'foo', 'bar.git', 'HEAD'))

def test_push_inits_if_needed_existsWithExtension():
    tmp = util.maketemp()
    cfg = RawConfigParser()
    cfg.add_section('gitosis')
    repositories = os.path.join(tmp, 'repositories')
    os.mkdir(repositories)
    cfg.set('gitosis', 'repositories', repositories)
    cfg.add_section('group foo')
    cfg.set('group foo', 'members', 'jdoe')
    cfg.set('group foo', 'writable', 'foo')
    os.mkdir(os.path.join(repositories, 'foo.git'))
    dcontrol.serve(
        cfg=cfg,
        user='jdoe',
        command="git-receive-pack 'foo'",
        )
    eq(os.listdir(repositories), ['foo.git'])
    # it should *not* have HEAD here as we just mkdirred it and didn't
    # create it properly, and the mock repo didn't have anything in
    # it.. having HEAD implies serve ran git init, which is supposed
    # to be unnecessary here
    eq(os.listdir(os.path.join(repositories, 'foo.git')), [])

def test_push_inits_no_stdout_spam():
    # git init has a tendency to spew to stdout, and that confuses
    # e.g. a git push
    tmp = util.maketemp()
    cfg = RawConfigParser()
    cfg.add_section('gitosis')
    repositories = os.path.join(tmp, 'repositories')
    os.mkdir(repositories)
    cfg.set('gitosis', 'repositories', repositories)
    generated = os.path.join(tmp, 'generated')
    os.mkdir(generated)
    cfg.set('gitosis', 'generate-files-in', generated)
    cfg.add_section('group foo')
    cfg.set('group foo', 'members', 'jdoe')
    cfg.set('group foo', 'writable', 'foo')
    old_stdout = os.dup(1)
    try:
        new_stdout = os.tmpfile()
        os.dup2(new_stdout.fileno(), 1)
        dcontrol.serve(
            cfg=cfg,
            user='jdoe',
            command="git-receive-pack 'foo'",
            )
    finally:
        os.dup2(old_stdout, 1)
        os.close(old_stdout)
    new_stdout.seek(0)
    got = new_stdout.read()
    new_stdout.close()
    eq(got, '')
    eq(os.listdir(repositories), ['foo.git'])
    assert os.path.isfile(os.path.join(repositories, 'foo.git', 'HEAD'))

def test_push_inits_sets_description():
    tmp = util.maketemp()
    cfg = RawConfigParser()
    cfg.add_section('gitosis')
    repositories = os.path.join(tmp, 'repositories')
    os.mkdir(repositories)
    cfg.set('gitosis', 'repositories', repositories)
    generated = os.path.join(tmp, 'generated')
    os.mkdir(generated)
    cfg.set('gitosis', 'generate-files-in', generated)
    cfg.add_section('group foo')
    cfg.set('group foo', 'members', 'jdoe')
    cfg.set('group foo', 'writable', 'foo')
    cfg.add_section('repo foo')
    cfg.set('repo foo', 'description', 'foodesc')
    dcontrol.serve(
        cfg=cfg,
        user='jdoe',
        command="git-receive-pack 'foo'",
        )
    eq(os.listdir(repositories), ['foo.git'])
    path = os.path.join(repositories, 'foo.git', 'description')
    assert os.path.exists(path)
    got = util.readFile(path)
    eq(got, 'foodesc\n')

def test_push_inits_updates_projects_list():
    tmp = util.maketemp()
    cfg = RawConfigParser()
    cfg.add_section('gitosis')
    repositories = os.path.join(tmp, 'repositories')
    os.mkdir(repositories)
    cfg.set('gitosis', 'repositories', repositories)
    generated = os.path.join(tmp, 'generated')
    os.mkdir(generated)
    cfg.set('gitosis', 'generate-files-in', generated)
    cfg.add_section('group foo')
    cfg.set('group foo', 'members', 'jdoe')
    cfg.set('group foo', 'writable', 'foo')
    cfg.add_section('repo foo')
    cfg.set('repo foo', 'gitweb', 'yes')
    os.mkdir(os.path.join(repositories, 'gitosis-admin.git'))
    dcontrol.serve(
        cfg=cfg,
        user='jdoe',
        command="git-receive-pack 'foo'",
        )
    eq(
        sorted(os.listdir(repositories)),
        sorted(['foo.git', 'gitosis-admin.git']),
        )
    path = os.path.join(generated, 'projects.list')
    assert os.path.exists(path)
    got = util.readFile(path)
    eq(got, 'foo.git\n')

def test_push_inits_sets_export_ok():
    tmp = util.maketemp()
    cfg = RawConfigParser()
    cfg.add_section('gitosis')
    repositories = os.path.join(tmp, 'repositories')
    os.mkdir(repositories)
    cfg.set('gitosis', 'repositories', repositories)
    generated = os.path.join(tmp, 'generated')
    os.mkdir(generated)
    cfg.set('gitosis', 'generate-files-in', generated)
    cfg.add_section('group foo')
    cfg.set('group foo', 'members', 'jdoe')
    cfg.set('group foo', 'writable', 'foo')
    cfg.add_section('repo foo')
    cfg.set('repo foo', 'daemon', 'yes')
    dcontrol.serve(
        cfg=cfg,
        user='jdoe',
        command="git-receive-pack 'foo'",
        )
    eq(os.listdir(repositories), ['foo.git'])
    path = os.path.join(repositories, 'foo.git', 'git-daemon-export-ok')
    assert os.path.exists(path)

def test_absolute():
    # as the only convenient way to use non-standard SSH ports with
    # git is via the ssh://user@host:port/path syntax, and that syntax
    # forces absolute urls, just force convert absolute paths to
    # relative paths; you'll never really want absolute paths via
    # gitosis, anyway.
    tmp = util.maketemp()
    repository.init(os.path.join(tmp, 'foo.git'))
    cfg = RawConfigParser()
    cfg.add_section('gitosis')
    cfg.set('gitosis', 'repositories', tmp)
    cfg.add_section('group foo')
    cfg.set('group foo', 'members', 'jdoe')
    cfg.set('group foo', 'readonly', 'foo')
    got = dcontrol.serve(
        cfg=cfg,
        user='jdoe',
        command="git-upload-pack '/foo'",
        )
    eq(got, "git-upload-pack '%s/foo.git'" % tmp)

def test_typo_writeable():
    tmp = util.maketemp()
    repository.init(os.path.join(tmp, 'foo.git'))
    cfg = RawConfigParser()
    cfg.add_section('gitosis')
    cfg.set('gitosis', 'repositories', tmp)
    cfg.add_section('group foo')
    cfg.set('group foo', 'members', 'jdoe')
    cfg.set('group foo', 'writeable', 'foo')
    log = logging.getLogger('dcontrol.serve')
    buf = StringIO()
    handler = logging.StreamHandler(buf)
    log.addHandler(handler)
    try:
        got = dcontrol.serve(
            cfg=cfg,
            user='jdoe',
            command="git-receive-pack 'foo'",
            )
    finally:
        log.removeHandler(handler)
    eq(got, "git-receive-pack '%s/foo.git'" % tmp)
    handler.flush()
    eq(
        buf.getvalue(),
        "Repository 'foo' config has typo \"writeable\", shou"
        +"ld be \"writable\"\n",
        )

def test_dcontrol1():
    tmp = util.maketemp()
    projname = 'foo'

    git_dir = os.path.join(tmp, projname+'.git')    
    repository.init(path=git_dir)
    repository.fast_import(
        git_dir=git_dir,
        committer='John Doe 2 <jdoe@example.com>',
        commit_msg="""\
Allow jdoe write access to foo
""",
        files=[
            ('foo', 'content'),
            ('bar/quux', 'another'),
            ],
        )
    
    print git_dir
    #export = os.path.join(tmp, 'export2')
    #varsites = os.path.join(tmp, 'var', 'sites', projname)
    #print "Export2: " + export
    #print git_dir
    #repository.export2(git_dir=git_dir, path=varsites)
    #eq(sorted(os.listdir(varsites)),
    #   sorted(['foo', 'bar']))
    #eq(readFile(os.path.join(varsites, 'foo')), 'content')
    #eq(os.listdir(os.path.join(varsites, 'bar')), ['quux'])
    #eq(readFile(os.path.join(varsites, 'bar', 'quux')), 'another')
    child = subprocess.Popen(
        args=[
            'git',
            '--git-dir=%s' % git_dir,
            'cat-file',
            'commit',
            'HEAD',
            ],
        cwd=git_dir,
        stdout=subprocess.PIPE,
        close_fds=True,
        )
    got = child.stdout.read().splitlines()
    returncode = child.wait()
    if returncode != 0:
        raise RuntimeError('git exit status %d' % returncode)
    eq(got[0].split(None, 1)[0], 'tree')
    eq(got[1].rsplit(None, 2)[0],
       'author John Doe 2 <jdoe@example.com>')
    eq(got[2].rsplit(None, 2)[0],
       'committer John Doe 2 <jdoe@example.com>')
    eq(got[3], '')
    eq(got[4], 'Allow jdoe write access to foo')
    eq(got[5:], [])
    
    '''
    cfg = RawConfigParser()
    cfg.add_section('gitosis')
    repositories = os.path.join(tmp, 'repositories')
    os.mkdir(repositories)
    cfg.set('gitosis', 'repositories', repositories)
    generated = os.path.join(tmp, 'generated')
    os.mkdir(generated)
    cfg.set('gitosis', 'generate-files-in', generated)
    cfg.add_section('group foo2')
    cfg.set('group foo2', 'members', 'jdoe')
    cfg.set('group foo2', 'writable', 'foo2')
    cfg.add_section('repo foo2')
    cfg.set('repo foo2', 'daemon', 'yes')
    dcontrol.serve(
        cfg=cfg,
        user='jdoe',
        command="git-receive-pack 'foo2'",
        )
    eq(os.listdir(repositories), ['foo2.git'])
    path = os.path.join(repositories, 'foo2.git', 'git-daemon-export-ok')
    assert os.path.exists(path)
    
    mirror_path = os.path.join(repositories, 'foo2.git')
    repository.mirror(git_dir, mirror_path)
    '''

    #exportvar = os.path.join(tmp, 'var2', 'sites')
    #repository.export2(
    #    git_dir=mirror_path,
    #    path=exportvar,
    #    )
    #eq(os.listdir(export),
    #   ['foo'])
    
def test_buildhook():
    buildhook.notify('asdf')
 
