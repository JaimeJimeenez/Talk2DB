import { ComponentFixture, TestBed } from '@angular/core/testing';
import { Component } from '@angular/core';

import { Button } from './button';
import { IButton } from '@interfaces/components/button';
import { provideLucideIcons, LucidePlus, LucideArrowRight } from '@lucide/angular';

@Component({
  template: `<talk2db-button [button]="button" />`,
  imports: [Button],
})
class TestHostComponent {
  button: IButton | null = null;
}

describe('Button', () => {
  let component: Button;
  let fixture: ComponentFixture<Button>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [Button, TestHostComponent],
      providers: [provideLucideIcons(LucidePlus, LucideArrowRight)],
    }).compileComponents();

    fixture = TestBed.createComponent(Button);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should have null button input by default', () => {
    expect(component.button).toBeNull();
  });

  it('should not render anything when button is null', () => {
    const compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.querySelector('button')).toBeNull();
  });

  describe('when button input is provided via host', () => {
    let hostFixture: ComponentFixture<TestHostComponent>;
    let hostComponent: TestHostComponent;
    let mockButton: IButton;

    beforeEach(async () => {
      mockButton = {
        label: 'Click me',
        disabled: false,
        onClick: vi.fn(),
      };

      hostFixture = TestBed.createComponent(TestHostComponent);
      hostComponent = hostFixture.componentInstance;

      hostComponent.button = mockButton;
      hostFixture.detectChanges();
      await hostFixture.whenStable();
    });

    it('should render the button element', () => {
      const buttonEl = hostFixture.nativeElement.querySelector('button');
      expect(buttonEl).toBeTruthy();
    });

    it('should display the label text', () => {
      const span = hostFixture.nativeElement.querySelector('span');
      expect(span?.textContent).toBe('Click me');
    });

    it('should not be disabled when disabled is false', () => {
      const buttonEl = hostFixture.nativeElement.querySelector('button') as HTMLButtonElement;
      expect(buttonEl.disabled).toBe(false);
    });

    it('should call onClick when button is clicked', () => {
      const buttonEl = hostFixture.nativeElement.querySelector('button') as HTMLButtonElement;
      buttonEl.click();

      expect(mockButton.onClick).toHaveBeenCalledTimes(1);
    });

    it('should not render icons when neither startIcon nor endIcon are provided', () => {
      const icons = hostFixture.nativeElement.querySelectorAll('talk2db-icon');
      expect(icons.length).toBe(0);
    });
  });

  describe('button disabled state', () => {
    let hostFixture: ComponentFixture<TestHostComponent>;
    let hostComponent: TestHostComponent;

    it('should be disabled when disabled is true', async () => {
      hostFixture = TestBed.createComponent(TestHostComponent);
      hostComponent = hostFixture.componentInstance;

      hostComponent.button = {
        label: 'Disabled',
        disabled: true,
        onClick: vi.fn(),
      };
      hostFixture.detectChanges();
      await hostFixture.whenStable();

      const buttonEl = hostFixture.nativeElement.querySelector('button') as HTMLButtonElement;
      expect(buttonEl.disabled).toBe(true);
    });
  });

  describe('button CSS class', () => {
    let hostFixture: ComponentFixture<TestHostComponent>;
    let hostComponent: TestHostComponent;

    it('should apply CSS class from button config', async () => {
      hostFixture = TestBed.createComponent(TestHostComponent);
      hostComponent = hostFixture.componentInstance;

      hostComponent.button = {
        label: 'Styled',
        disabled: false,
        onClick: vi.fn(),
        class: 'new_chat-button',
      };
      hostFixture.detectChanges();
      await hostFixture.whenStable();

      const buttonEl = hostFixture.nativeElement.querySelector('button') as HTMLButtonElement;
      expect(buttonEl.classList.contains('new_chat-button')).toBe(true);
    });
  });

  describe('button with icons', () => {
    let hostFixture: ComponentFixture<TestHostComponent>;
    let hostComponent: TestHostComponent;

    it('should render startIcon when provided', async () => {
      hostFixture = TestBed.createComponent(TestHostComponent);
      hostComponent = hostFixture.componentInstance;

      hostComponent.button = {
        label: 'With start icon',
        disabled: false,
        onClick: vi.fn(),
        startIcon: { name: 'plus', size: 16 },
      };
      hostFixture.detectChanges();
      await hostFixture.whenStable();

      const icons = hostFixture.nativeElement.querySelectorAll('talk2db-icon');
      expect(icons.length).toBe(1);
    });

    it('should render endIcon when provided', async () => {
      hostFixture = TestBed.createComponent(TestHostComponent);
      hostComponent = hostFixture.componentInstance;

      hostComponent.button = {
        label: 'With end icon',
        disabled: false,
        onClick: vi.fn(),
        endIcon: { name: 'arrow-right', size: 16 },
      };
      hostFixture.detectChanges();
      await hostFixture.whenStable();

      const icons = hostFixture.nativeElement.querySelectorAll('talk2db-icon');
      expect(icons.length).toBe(1);
    });

    it('should render both icons when startIcon and endIcon are provided', async () => {
      hostFixture = TestBed.createComponent(TestHostComponent);
      hostComponent = hostFixture.componentInstance;

      hostComponent.button = {
        label: 'With both icons',
        disabled: false,
        onClick: vi.fn(),
        startIcon: { name: 'plus', size: 16 },
        endIcon: { name: 'arrow-right', size: 16 },
      };
      hostFixture.detectChanges();
      await hostFixture.whenStable();

      const icons = hostFixture.nativeElement.querySelectorAll('talk2db-icon');
      expect(icons.length).toBe(2);
    });
  });
});
