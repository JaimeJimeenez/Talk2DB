import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';

import { Sidebar } from '@components/sidebar/sidebar';
import { Header } from '@components/header/header';

@Component({
  selector: 'talk2db-main',
  imports: [RouterOutlet, Sidebar, Header],
  templateUrl: './main.html',
  styleUrl: './main.scss',
})
export class Main {}
