import { ComponentFixture, TestBed } from '@angular/core/testing';
import { Component } from '@angular/core';
import { provideLucideIcons, LucideBot } from '@lucide/angular';

import { Answer } from './answer';

@Component({
  template: `<talk2db-answer [content]="content" [timestamp]="timestamp" />`,
  imports: [Answer],
})
class TestHostComponent {
  content = 'Test answer from AI';
  timestamp = new Date();
}

describe('Answer', () => {
  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [Answer, TestHostComponent],
      providers: [provideLucideIcons(LucideBot)],
    }).compileComponents();
  });

  it('should create via host', () => {
    const hostFixture = TestBed.createComponent(TestHostComponent);
    hostFixture.detectChanges();
    const answerEl = hostFixture.nativeElement.querySelector('talk2db-answer');
    expect(answerEl).toBeTruthy();
  });

  it('should display the content', () => {
    const hostFixture = TestBed.createComponent(TestHostComponent);
    hostFixture.detectChanges();
    const content = hostFixture.nativeElement.querySelector('.answer-content');
    expect(content?.textContent).toBe('Test answer from AI');
  });

  it('should render the bot avatar', () => {
    const hostFixture = TestBed.createComponent(TestHostComponent);
    hostFixture.detectChanges();
    const avatar = hostFixture.nativeElement.querySelector('.answer-avatar');
    expect(avatar).toBeTruthy();
  });
});
