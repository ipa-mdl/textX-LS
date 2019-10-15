import { inject, injectable } from "inversify";
import { join } from "path";
import { commands, window } from "vscode";
import {
  CMD_GENERATE_EXTENSION, CMD_GENERATE_SYNTAXES, CMD_GENERATOR_LIST, EXTENSION_GENERATOR_TARGET,
  EXTENSION_SYNTAX_HIGHLIGHT_TARGET, VSCE_COMMAND_PATH,
} from "../constants";
import { ITextXExtensionInstall, ITextXGenerator } from "../interfaces";
import TYPES from "../types";
import { mkdtempWrapper } from "../utils";
import { IExtensionService } from "./extensionService";
import { ISyntaxHighlightService } from "./SyntaxHighlightService";

export interface IGeneratorService {
  generateAndInstallExtension(projectName: string, editableMode: boolean): Promise<ITextXExtensionInstall>; // tslint:disable: max-line-length
  generateLanguagesSyntaxes(projectName: string): Promise<Map<string, string>>;
  getAll(): Promise<ITextXGenerator[]>;
  getByLanguage(languageName: string): Promise<ITextXGenerator[]>;
}

@injectable()
export class GeneratorService implements IGeneratorService {

  constructor(
    @inject(TYPES.ISyntaxHighlightService) private readonly syntaxHighlightService: ISyntaxHighlightService, // tslint:disable: max-line-length
    @inject(TYPES.IExtensionService) private readonly extensionService: IExtensionService,
  ) { }

  public async generateAndInstallExtension(
    projectName: string, editableMode: boolean = false,
  ): Promise<ITextXExtensionInstall> {

    return new Promise(async (resolve) => {
      mkdtempWrapper(async (folder) => {
        const cmdArgs = { project_name: projectName, vsix: 1, skip_keywords: editableMode, vsce: VSCE_COMMAND_PATH };

        const isGenerated = await commands.executeCommand(
          CMD_GENERATE_EXTENSION.external, EXTENSION_GENERATOR_TARGET, folder, cmdArgs);

        if (isGenerated) {
          const extensionPath = join(folder, projectName + ".vsix");

          try {
            await this.extensionService.install(extensionPath);

            if (editableMode) {
              const languageSyntaxes = await this.generateLanguagesSyntaxes(projectName);
              this.syntaxHighlightService.addLanguageKeywordsFromTextmate(languageSyntaxes);
              this.syntaxHighlightService.highlightAllEditorsDocument();
            }
          } catch (_) {
            window.showErrorMessage(`Installing extension for project '${projectName}' failed.`);
          }
        }

      });
    });
  }

  public async generateLanguagesSyntaxes(projectName: string): Promise<Map<string, string>> {
    return await commands.executeCommand(CMD_GENERATE_SYNTAXES.external, projectName,
      EXTENSION_SYNTAX_HIGHLIGHT_TARGET, { silent: 1 });
  }

  public async getAll(): Promise<ITextXGenerator[]> {
    const gens = await commands.executeCommand<ITextXGenerator[]>(CMD_GENERATOR_LIST.external);
    return gens || [];
  }

  public async getByLanguage(languageName: string): Promise<ITextXGenerator[]> {
    window.showWarningMessage("GeneratorService.getByLanguage is not implemented!");
    return [];
  }

}
