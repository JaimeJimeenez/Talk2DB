import { Routes } from '@angular/router';

export const routes: Routes = [
    { 
        path: '',
        loadComponent: () => import("@pages/main/main").then(component => component.Main)
    }
];