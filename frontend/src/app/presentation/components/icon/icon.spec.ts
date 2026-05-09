import { ComponentFixture, TestBed } from '@angular/core/testing';
import { Component } from '@angular/core';
import { provideLucideIcons, LucidePlus } from '@lucide/angular';

import { Icon } from './icon';
import { IIcon } from '@interfaces/components/icon';

@Component({
  template: `<talk2db-icon [icon]="icon" />`,
  imports: [Icon],
})
class TestHostComponent {
  icon: IIcon | null = null;
}

describe('Icon', () => {
  let component: Icon;
  let fixture: ComponentFixture<Icon>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [Icon],
      providers: [provideLucideIcons(LucidePlus)],
    }).compileComponents();

    fixture = TestBed.createComponent(Icon);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should have null icon input by default', () => {
    expect(component.icon()).toBeNull();
  });

  it('should not render svg when icon is null', () => {
    const compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.querySelector('svg')).toBeNull();
  });

  describe('with host component', () => {
    let hostFixture: ComponentFixture<TestHostComponent>;
    let hostComponent: TestHostComponent;

    beforeEach(async () => {
      hostFixture = TestBed.createComponent(TestHostComponent);
      hostComponent = hostFixture.componentInstance;
    });

    it('should render svg when icon input is provided', async () => {
      hostComponent.icon = { name: 'plus' };
      hostFixture.detectChanges();
      await hostFixture.whenStable();

      const svg = hostFixture.nativeElement.querySelector('svg');
      expect(svg).toBeTruthy();
    });

    it('should apply default size of 24 when size is not specified', async () => {
      hostComponent.icon = { name: 'plus' };
      hostFixture.detectChanges();
      await hostFixture.whenStable();

      const svg = hostFixture.nativeElement.querySelector('svg') as SVGElement;
      expect(svg).toBeTruthy();
      expect(svg.getAttribute('height')).toBe('24');
      expect(svg.getAttribute('width')).toBe('24');
    });

    it('should apply custom size when specified', async () => {
      hostComponent.icon = { name: 'plus', size: 16 };
      hostFixture.detectChanges();
      await hostFixture.whenStable();

      const svg = hostFixture.nativeElement.querySelector('svg') as SVGElement;
      expect(svg).toBeTruthy();
      expect(svg.getAttribute('height')).toBe('16');
      expect(svg.getAttribute('width')).toBe('16');
    });

    it('should apply default strokeWidth of 2 when not specified', async () => {
      hostComponent.icon = { name: 'plus' };
      hostFixture.detectChanges();
      await hostFixture.whenStable();

      const svg = hostFixture.nativeElement.querySelector('svg') as SVGElement;
      expect(svg).toBeTruthy();
      expect(svg.getAttribute('stroke-width')).toBe('2');
    });

    it('should apply custom strokeWidth when specified', async () => {
      hostComponent.icon = { name: 'plus', strokeWidth: 3 };
      hostFixture.detectChanges();
      await hostFixture.whenStable();

      const svg = hostFixture.nativeElement.querySelector('svg') as SVGElement;
      expect(svg).toBeTruthy();
      expect(svg.getAttribute('stroke-width')).toBe('3');
    });

    it('should apply title when specified', async () => {
      hostComponent.icon = { name: 'plus', title: 'Add item' };
      hostFixture.detectChanges();
      await hostFixture.whenStable();

      const svg = hostFixture.nativeElement.querySelector('svg');
      expect(svg).toBeTruthy();
    });

    it('should hide svg from accessibility when no title', async () => {
      hostComponent.icon = { name: 'plus' };
      hostFixture.detectChanges();
      await hostFixture.whenStable();

      const svg = hostFixture.nativeElement.querySelector('svg') as SVGElement;
      expect(svg.getAttribute('aria-hidden')).toBe('true');
    });
  });
});
