import { Routes } from '@angular/router';

export const routes: Routes = [
    {
        path: '',
        loadComponent: () => import("@pages/main/main").then(component => component.Main),
        children: [
            {
                path: '',
                redirectTo: 'chat',
                pathMatch: 'full'
            },
            {
                path: 'chat',
                loadComponent: () => import("@pages/chat/chat").then(component => component.Chat)
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
