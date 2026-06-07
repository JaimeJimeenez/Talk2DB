import { Routes } from '@angular/router';

import { authGuard } from '@infrastructure/guards/auth';

export const routes: Routes = [
    {
        path: '',
        canActivateChild: [authGuard],
        loadComponent: () => import("@pages/main/main").then(component => component.Main),
        children: [
            {
                path: '',
                redirectTo: 'new-chat',
                pathMatch: 'full'
            },
            {
                path: 'new-chat',
                loadComponent: () => import("@pages/new-chat/new-chat").then(component => component.NewChat)
            },
            {
                path: 'conversations/:conversationId',
                loadComponent: () => import("@pages/chat/chat").then(component => component.Chat)
            },
            {
                path: 'metrics',
                loadComponent: () => import("@pages/metrics/metrics").then(component => component.Metrics)
            },
            {
                path: 'schema',
                loadComponent: () => import("@pages/schema/schema").then(component => component.Schema)
            },
        ]
    },
    {
        path: 'signup',
        loadComponent: () => import("@pages/signup/signup").then(component => component.Signup)
    },
    {
        path: 'login',
        loadComponent: () => import("@pages/login/login").then(component => component.Login)
    }
];
