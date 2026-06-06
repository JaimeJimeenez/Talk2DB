import { ComponentFixture, TestBed } from '@angular/core/testing';
import { Component } from '@angular/core';

import { Question } from './question';

@Component({
  template: `<talk2db-question [content]="content" />`,
  imports: [Question],
})
class TestHostComponent {
  content = 'Test user question';
}

describe('Question', () => {
  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [Question, TestHostComponent],
    }).compileComponents();
  });

  it('should create via host', () => {
    const hostFixture = TestBed.createComponent(TestHostComponent);
    hostFixture.detectChanges();
    const questionEl = hostFixture.nativeElement.querySelector('talk2db-question');
    expect(questionEl).toBeTruthy();
  });

  it('should display the content', () => {
    const hostFixture = TestBed.createComponent(TestHostComponent);
    hostFixture.detectChanges();
    const bubble = hostFixture.nativeElement.querySelector('.question-bubble p');
    expect(bubble?.textContent).toBe('Test user question');
  });
});
