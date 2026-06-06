import { ApplicationConfig, provideBrowserGlobalErrorListeners } from '@angular/core';
import { provideHttpClient, withInterceptors } from '@angular/common/http';
import { provideRouter } from '@angular/router';

import { 
  LucideArrowUp,
  LucideBot,
  LucidePlus,
  LucideCircleX,
  LucideX,
  provideLucideIcons, 
  LucideTriangleAlert,
  LucideInfo,
  LucideBadgeCheck,
  LucideChevronDown,
  LucideDatabase,
  LucideChartLine,
  LucideHistory,
  LucideTable,
  LucideRows3,
  LucideBarChart3,
  LucideCode2,
  LucideCopy,
  LucideCheck,
  LucideArrowRight
} from '@lucide/angular';

import { ConversationPort } from '@domain/ports/conversation';
import { QuerySchemaPort } from '@domain/ports/query-schema';
import { RagMetricsPort } from '@domain/ports/rag-metrics';
import { UserPort } from '@domain/ports/user';

import { ConversationAdapter } from '@infrastructure/adapters/conversation';
import { QuerySchemaAdapter } from '@infrastructure/adapters/query-schema';
import { RagMetricsAdapter } from '@infrastructure/adapters/rag-metrics';
import { routes } from "@infrastructure/routes/routes";
import { UserAdapter } from '@infrastructure/adapters/user';
import { tokenInterceptor } from '@infrastructure/interceptors/token';

export const appConfig: ApplicationConfig = {
  providers: [
    provideBrowserGlobalErrorListeners(),
    provideRouter(routes),
    provideHttpClient(withInterceptors([tokenInterceptor])),
    provideLucideIcons(
      LucidePlus,
      LucideArrowUp,
      LucideBot,
      LucideCircleX,
      LucideX,
      LucideTriangleAlert,
      LucideInfo,
      LucideBadgeCheck,
      LucideChevronDown,
      LucideDatabase,
      LucideChartLine,
      LucideHistory,
      LucideTable,
      LucideRows3,
      LucideBarChart3,
      LucideCode2,
      LucideCopy,
      LucideCheck,
      LucideArrowRight
    ),
    { provide: ConversationPort, useClass: ConversationAdapter },
    { provide: QuerySchemaPort, useClass: QuerySchemaAdapter },
    { provide: RagMetricsPort, useClass: RagMetricsAdapter },
    { provide: UserPort, useClass: UserAdapter }
  ]
};
