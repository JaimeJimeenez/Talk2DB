import { ComponentFixture, TestBed } from '@angular/core/testing';
import { Component } from '@angular/core';
import {
  LucideBarChart3,
  LucideCheck,
  LucideCode2,
  LucideCopy,
  LucideRows3,
  LucideTable,
  LucideX,
  provideLucideIcons,
} from '@lucide/angular';

import { Artifact } from './artifact';
import { QueryArtifact } from '@domain/models/message';

@Component({
  template: `<talk2db-artifact [artifact]="artifact" />`,
  imports: [Artifact],
})
class TestHostComponent {
  artifact: QueryArtifact = {
    id: 'artifact-1',
    title: 'Sales',
    summary: 'Sales summary',
    type: 'query_result',
    generatedFrom: 'show sales',
    sql: 'SELECT name, total FROM sales LIMIT 100',
    columns: [{ name: 'name', type: 'str' }, { name: 'total', type: 'int' }],
    rows: [{ name: 'Alice', total: 1200 }],
    rowCount: 1,
    truncated: false,
    error: null,
  };
}

describe('Artifact', () => {
  let fixture: ComponentFixture<TestHostComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [Artifact, TestHostComponent],
      providers: [
        provideLucideIcons(
          LucideTable,
          LucideRows3,
          LucideBarChart3,
          LucideCode2,
          LucideCopy,
          LucideCheck,
          LucideX,
        ),
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(TestHostComponent);
    await fixture.whenStable();
  });

  it('should create', () => {
    fixture.detectChanges();
    expect(fixture.nativeElement.querySelector('talk2db-artifact')).toBeTruthy();
  });

  it('shows table view by default even when rows can be charted', () => {
    fixture.detectChanges();

    const table = fixture.nativeElement.querySelector('talk2db-artifact-table');
    const activeTab = fixture.nativeElement.querySelector('.artifact-tabs button.active');

    expect(table).toBeTruthy();
    expect(activeTab?.textContent).toContain('Tabla');
  });
});
