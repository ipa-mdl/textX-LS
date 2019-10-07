import "reflect-metadata";

import { Container } from "inversify";
import { EventService, IEventService } from "./services/eventService";
import { GeneratorService, IGeneratorService } from "./services/generatorService";
import { IProjectService, ProjectService } from "./services/projectService";
import {
  ISyntaxHighlightService,
  SyntaxHighlightService,
} from "./services/SyntaxHighlightService";
import { IWatcherService, WatcherService } from "./services/watcherService";
import TYPES from "./types";
import {
  IGeneratorProvider, ILanguageProvider, TextXGeneratorProvider, TextXLanguageProvider,
} from "./ui/explorer";

const container = new Container();
// Services
container.bind<IEventService>(TYPES.IEventService).to(EventService).inSingletonScope();
container.bind<IGeneratorService>(TYPES.IGeneratorService).to(GeneratorService);
container.bind<IProjectService>(TYPES.IProjectService).to(ProjectService);
container.bind<ISyntaxHighlightService>(TYPES.ISyntaxHighlightService).to(SyntaxHighlightService).inSingletonScope(); // tslint:disable: max-line-length
container.bind<IWatcherService>(TYPES.IWatcherService).to(WatcherService).inSingletonScope();

// Tree data providers
container.bind<IGeneratorProvider>(TYPES.IGeneratorProvider).to(TextXGeneratorProvider).inSingletonScope();
container.bind<ILanguageProvider>(TYPES.ILanguageProvider).to(TextXLanguageProvider).inSingletonScope();

export default container;
