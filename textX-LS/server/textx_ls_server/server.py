import sys

from pygls.features import (
    TEXT_DOCUMENT_DID_CHANGE,
    TEXT_DOCUMENT_DID_CLOSE,
    TEXT_DOCUMENT_DID_OPEN,
)
from pygls.server import LanguageServer
from pygls.types import (
    DidChangeTextDocumentParams,
    DidCloseTextDocumentParams,
    DidOpenTextDocumentParams,
    MessageType,
)

from textx_ls_core.features.generators import (
    generate_extension,
    generate_syntaxes,
    get_generators,
)
from textx_ls_core.features.projects import (
    get_projects,
    install_project_async,
    uninstall_project_async,
)
from textx_ls_core.utils import compare_project_names

from .features.diagnostics import send_diagnostics
from .protocol import TextXDocument, TextXProtocol
from .utils import skip_not_supported_langs


class TextXLanguageServer(LanguageServer):
    CMD_GENERATE_EXTENSION = "textx/generateExtension"
    CMD_GENERATE_SYNTAXES = "textx/generateSyntaxes"
    CMD_GENERATOR_LIST = "textx/getGenerators"
    CMD_PROJECT_INSTALL = "textx/installProject"
    CMD_PROJECT_LIST = "textx/getProjects"
    CMD_PROJECT_SCAFFOLD = "textx/scaffoldProject"
    CMD_PROJECT_UNINSTALL = "textx/uninstallProject"
    CMD_VALIDATE_DOCUMENTS = "textx/validateDocuments"

    def __init__(self):
        super().__init__(protocol_cls=TextXProtocol)
        self.python_path = sys.executable


textx_server = TextXLanguageServer()


@textx_server.command(TextXLanguageServer.CMD_GENERATE_EXTENSION)
def cmd_generate_extension(ls: TextXLanguageServer, params):
    target = params[0]
    dest_dir = params[1]
    cmd_args = params[2]

    try:
        generate_extension(target, dest_dir, **cmd_args._asdict())
        return True
    except Exception:
        return False


@textx_server.command(TextXLanguageServer.CMD_GENERATE_SYNTAXES)
def cmd_generate_syntaxes(ls: TextXLanguageServer, params):
    project_name = params[0]
    target = params[1]
    return generate_syntaxes(project_name, target)


@textx_server.command(TextXLanguageServer.CMD_GENERATOR_LIST)
@textx_server.thread()
def cmd_generator_list(ls: TextXLanguageServer, params):
    return get_generators()


@textx_server.command(TextXLanguageServer.CMD_PROJECT_INSTALL)
async def cmd_project_install(ls: TextXLanguageServer, params):
    folder_or_wheel = params[0]
    editable = params[1]

    ls.show_message("Installing project from {}".format(folder_or_wheel))
    is_installed, project_name, dist_location = await install_project_async(
        folder_or_wheel, ls.python_path, editable, ls.show_message_log
    )

    if is_installed:
        ls.show_message("Project {} is successfully installed.".format(project_name))
    else:
        ls.show_message(
            "Failed to install project {}.".format(project_name), MessageType.Error
        )

    return project_name, dist_location if is_installed else None, dist_location


@textx_server.command(TextXLanguageServer.CMD_PROJECT_LIST)
@textx_server.thread()
def cmd_project_list(ls: TextXLanguageServer, params):
    load_langs = params[0] if len(params) == 1 else True
    return get_projects(load_langs)


@textx_server.command(TextXLanguageServer.CMD_PROJECT_SCAFFOLD)
def cmd_project_scaffold(ls: TextXLanguageServer, params):
    ls.show_message("Not implemented")


@textx_server.command(TextXLanguageServer.CMD_PROJECT_UNINSTALL)
async def cmd_project_uninstall(ls: TextXLanguageServer, params):
    project_name = params[0]

    ls.show_message("Uninstalling project {}".format(project_name))
    is_uninstalled = await uninstall_project_async(
        project_name, ls.python_path, ls.show_message_log
    )

    if is_uninstalled:
        ls.show_message("Project {} is successfully uninstalled.".format(project_name))
    else:
        ls.show_message(
            "Failed to uninstall project {}.".format(project_name), MessageType.Error
        )

    return is_uninstalled


@textx_server.command(TextXLanguageServer.CMD_VALIDATE_DOCUMENTS)
def cmd_validate_documents(ls: TextXLanguageServer, params):
    project_name = params[0]
    for doc in ls.workspace.documents.values():
        if project_name and compare_project_names(project_name, doc.project_name):
            send_diagnostics(ls, doc)


@textx_server.feature(TEXT_DOCUMENT_DID_CHANGE)
@skip_not_supported_langs
def doc_change(
    ls: TextXLanguageServer, params: DidChangeTextDocumentParams, doc: TextXDocument
):
    """Validates model on document text change."""
    send_diagnostics(ls, doc)


@textx_server.feature(TEXT_DOCUMENT_DID_CLOSE)
def doc_close(ls: TextXLanguageServer, params: DidCloseTextDocumentParams):
    """Clear diagnostics on document close event."""
    ls.publish_diagnostics(params.textDocument.uri, [])


@textx_server.feature(TEXT_DOCUMENT_DID_OPEN)
@skip_not_supported_langs
def doc_open(
    ls: TextXLanguageServer, params: DidOpenTextDocumentParams, doc: TextXDocument
):
    """Validates model on document text change."""
    send_diagnostics(ls, doc)
