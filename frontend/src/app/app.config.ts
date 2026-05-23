import { ApplicationConfig, provideBrowserGlobalErrorListeners } from '@angular/core';
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
  LucideBadgeCheck
} from '@lucide/angular';

import { ConversationPort } from '@domain/ports/conversation';
import { UserPort } from '@domain/ports/user';

import { ConversationAdapter } from '@infrastructure/adapters/conversation';
import { routes } from "@infrastructure/routes/routes";
import { UserAdapter } from '@infrastructure/adapters/user';

export const appConfig: ApplicationConfig = {
  providers: [
    provideBrowserGlobalErrorListeners(),
    provideRouter(routes),
    provideLucideIcons(
      LucidePlus,
      LucideArrowUp,
      LucideBot,
      LucideCircleX,
      LucideX,
      LucideTriangleAlert,
      LucideInfo,
      LucideBadgeCheck
    ),
    { provide: ConversationPort, useClass: ConversationAdapter },
    { provide: UserPort, useClass: UserAdapter }
  ]
};
