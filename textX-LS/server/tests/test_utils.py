import mock
import pytest
from pygls.types import DidOpenTextDocumentParams, TextDocumentItem

from textx_ls_server import utils

GET_FILE_EXTENSION_TARGET = 'textx_ls_server.utils.get_file_extension'


@pytest.fixture(scope='module')
def lang_extensions():
    return ('tx', 'textxfile')


@pytest.fixture(scope='module')
def languages():
    class FakeTemplate:
        def __init__(self, name):
            self.name = name

    return {
        'tx': FakeTemplate('textx'),
        'textxfile': FakeTemplate('textxfile')
    }


@pytest.fixture(scope='module')
def params():
    return DidOpenTextDocumentParams(TextDocumentItem('textxfile', '', 1, ''))


def test_call_with_lang_template(languages, params):
    def to_wrap(ls, params, **kwargs):
        return kwargs
    wrapped = utils.call_with_lang_template(to_wrap, languages)
    ret_kwargs = wrapped(None, params)

    assert 'lang_temp' in ret_kwargs


def test_call_with_lang_template_should_return_none(languages, params):
    def to_wrap(ls, params, **kwargs):
        return kwargs
    wrapped = utils.call_with_lang_template(to_wrap, {})
    ret_kwargs = wrapped(None, params)

    assert ret_kwargs is None


@pytest.mark.parametrize("uri, expected", [
    ('/users/test/testfile.rst', False),
    ('/users/test/textxfile', True),
    ('/users/test/grammar.tx', True)
])
def test_is_ext_supported(lang_extensions, uri, expected):
    assert utils.is_ext_supported(uri, lang_extensions) is expected


def test_skip_not_supported_langs(params):
    class LS:
        class Workspace:
            def __init__(self):
                self.documents = {}

        def __init__(self):
            self.workspace = self.Workspace()

    to_wrap = mock.Mock()
    wrapped = utils.skip_not_supported_langs(to_wrap)
    wrapped(LS(), params)

    to_wrap.assert_not_called()
