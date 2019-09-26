import { ITokenColorSettings } from "./interfaces";

export type TokenColors = Map<string, ITokenColorSettings>;

const TYPES = {
  GeneratorNode: Symbol("GeneratorNode"),
  IEventService: Symbol("IEventService"),
  IGeneratorProvider: Symbol("IGeneratorProvider"),
  IGeneratorService: Symbol("IGeneratorService"),
  ILanguageProvider: Symbol("ILanguageProvider"),
  IProjectService: Symbol("IProjectService"),
  IWatcherService: Symbol("IWatcherService"),
  TextXNode: Symbol("LanguageNode"),
};

export default TYPES;
