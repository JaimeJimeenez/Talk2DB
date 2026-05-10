import { ApplicationConfig, provideBrowserGlobalErrorListeners } from '@angular/core';
import { provideRouter } from '@angular/router';

import { routes } from "@infrastructure/routes/routes";
import { LucideArrowUp, LucidePlus, provideLucideIcons } from '@lucide/angular';

export const appConfig: ApplicationConfig = {
  providers: [
    provideBrowserGlobalErrorListeners(),
    provideRouter(routes),
    provideLucideIcons(LucidePlus, LucideArrowUp)
  ]
};
