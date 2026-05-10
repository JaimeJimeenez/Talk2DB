import { Component } from '@angular/core';
import { Prompt } from "@components/prompt/prompt";

@Component({
  selector: 'talk2db-chat',
  imports: [Prompt],
  templateUrl: './chat.html',
  styleUrl: './chat.scss',
})
export class Chat {}
