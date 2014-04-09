
import pytest

from melba.utils import parse_vcs_url

from .data import URL1

def test_parse_git_ssh_url():
    assert URL1 == "git@github.com:averagehuman/maths.averagehuman.org.git"
    kw = parse_vcs_url(URL1)
    assert kw["url"] == URL1
    assert kw["vcs"] == "git"
    assert kw["host"] == "github"
    assert kw["owner"] == "averagehuman"
    assert kw["repo"] == "maths.averagehuman.org"
    assert kw["slug"] == "github-averagehuman-maths-averagehuman-org-git"

