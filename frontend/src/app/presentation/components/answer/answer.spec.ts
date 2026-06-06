import { ComponentFixture, TestBed } from '@angular/core/testing';
import { Component } from '@angular/core';
import { LucideArrowRight, LucideBot, LucideTable, provideLucideIcons } from '@lucide/angular';

import { Answer } from './answer';
import { Message } from '@domain/models/message';

@Component({
  template: `<talk2db-answer [message]="message" />`,
  imports: [Answer],
})
class TestHostComponent {
  message: Message = {
    id: 'message-1',
    role: 'assistant',
    content: 'Test answer from AI',
    timestamp: new Date(),
  };
}

describe('Answer', () => {
  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [Answer, TestHostComponent],
      providers: [provideLucideIcons(LucideBot, LucideTable, LucideArrowRight)],
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

  it('renders an artifact link when the message has an artifact', () => {
    const hostFixture = TestBed.createComponent(TestHostComponent);
    hostFixture.componentInstance.message = {
      ...hostFixture.componentInstance.message,
      artifact: {
        id: 'artifact-1',
        title: 'Clientes activos',
        summary: 'Clientes activos encontrados.',
        type: 'query_result',
        generatedFrom: 'Muestra clientes activos',
        sql: 'SELECT id, name FROM ventas.customers LIMIT 100',
        columns: [{ name: 'name', type: 'str' }],
        rows: [{ name: 'Acme Retail' }],
        rowCount: 1,
        truncated: false,
        error: null,
      },
    };
    hostFixture.detectChanges();

    const artifactLink = hostFixture.nativeElement.querySelector('talk2db-artifact-link');
    expect(artifactLink?.textContent).toContain('Clientes activos');
  });
});
