import { Component, OnInit } from '@angular/core';
import { FormControl, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';

import { SUBMIT_PROMPT_BUTTON } from '@constants/components/prompt';
import { IButton } from '@interfaces/components/button';
import { Button } from "@components/button/button";

@Component({
  selector: 'talk2db-prompt',
  imports: [ReactiveFormsModule, Button],
  templateUrl: './prompt.html',
  styleUrl: './prompt.scss',
})
export class Prompt implements OnInit {
  promptForm: FormGroup = new FormGroup({});
  submitButton: IButton = SUBMIT_PROMPT_BUTTON;

  ngOnInit(): void {
    this._initializeForm();
  }

  onSubmit(): void {

  }

  private _initializeForm(): void {
    this.promptForm = new FormGroup({
      prompt: new FormControl('', [Validators.required])
    });
  }
}
