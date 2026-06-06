import { ComponentFixture, TestBed } from '@angular/core/testing';
import { LucideChevronDown, LucideHistory, provideLucideIcons } from '@lucide/angular';

import { Dropdown } from './dropdown';

describe('Dropdown', () => {
  let component: Dropdown;
  let fixture: ComponentFixture<Dropdown>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [Dropdown],
      providers: [provideLucideIcons(LucideChevronDown, LucideHistory)],
    }).compileComponents();

    fixture = TestBed.createComponent(Dropdown);
    component = fixture.componentInstance;
    fixture.componentRef.setInput('dropdown', {
      label: 'Consultas recientes',
      icon: { name: 'history', title: 'Consultas recientes', size: 18 },
      items: [{ id: 'conversation-1', label: 'Mock conversation' }],
      emptyLabel: 'Sin conversaciones recientes',
    });
    fixture.detectChanges();
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('renders label and items', () => {
    const compiled = fixture.nativeElement as HTMLElement;

    expect(compiled.textContent).toContain('Consultas recientes');
    expect(compiled.textContent).toContain('Mock conversation');
  });

  it('renders the selected item label in the trigger', () => {
    fixture.componentRef.setInput('selectedId', 'conversation-1');
    fixture.detectChanges();
    const compiled = fixture.nativeElement as HTMLElement;
    const trigger = compiled.querySelector('.dropdown-trigger');

    expect(trigger?.textContent).toContain('Mock conversation');
  });

  it('toggles the list', () => {
    const compiled = fixture.nativeElement as HTMLElement;
    const trigger = compiled.querySelector<HTMLButtonElement>('.dropdown-trigger');

    trigger?.click();
    fixture.detectChanges();

    expect(compiled.querySelector('.dropdown-list')).toBeNull();
  });

  it('emits selected item id', () => {
    const selected = vi.fn();
    component.selected.subscribe(selected);
    const compiled = fixture.nativeElement as HTMLElement;

    compiled.querySelector<HTMLButtonElement>('.dropdown-item')?.click();

    expect(selected).toHaveBeenCalledWith('conversation-1');
    expect(component.isOpen()).toBe(false);
  });

  it('does not open when disabled', () => {
    fixture.componentRef.setInput('disabled', true);
    fixture.detectChanges();
    const compiled = fixture.nativeElement as HTMLElement;
    const trigger = compiled.querySelector<HTMLButtonElement>('.dropdown-trigger');

    trigger?.click();
    fixture.detectChanges();

    expect(component.isOpen()).toBe(true);
  });
});
