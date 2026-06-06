import { ComponentFixture, TestBed } from '@angular/core/testing';

import { Chip } from './chip';

describe('Chip', () => {
  let component: Chip;
  let fixture: ComponentFixture<Chip>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [Chip],
    }).compileComponents();

    fixture = TestBed.createComponent(Chip);
    component = fixture.componentInstance;
    fixture.componentRef.setInput('label', 'ventas');
    fixture.detectChanges();
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('renders the label', () => {
    const chip = fixture.nativeElement.querySelector('.chip') as HTMLElement;

    expect(chip.textContent).toBe('ventas');
    expect(chip.getAttribute('title')).toBe('ventas');
  });
});
