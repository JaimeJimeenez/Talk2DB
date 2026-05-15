import { ApplicationConfig, provideBrowserGlobalErrorListeners } from '@angular/core';
import { provideRouter } from '@angular/router';

import { routes } from "@infrastructure/routes/routes";
import { LucideArrowUp, LucideBot, LucidePlus, provideLucideIcons } from '@lucide/angular';

import { ConversationPort } from '@domain/ports/conversation';
import { MockConversationAdapter } from '@infrastructure/adapters/mock-conversation.adapter';

export const appConfig: ApplicationConfig = {
  providers: [
    provideBrowserGlobalErrorListeners(),
    provideRouter(routes),
    provideLucideIcons(LucidePlus, LucideArrowUp, LucideBot),
    
    { provide: ConversationPort, useClass: MockConversationAdapter },
  ]
};
