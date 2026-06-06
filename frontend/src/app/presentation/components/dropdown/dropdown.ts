import { ChangeDetectionStrategy, Component, OnInit, computed, input, output, signal } from '@angular/core';

import { Icon } from '@components/icon/icon';

import { IDropdown, IDropdownItem } from '@interfaces/components/dropdown';

@Component({
  selector: 'talk2db-dropdown',
  imports: [Icon],
  templateUrl: './dropdown.html',
  styleUrl: './dropdown.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class Dropdown implements OnInit {
  readonly dropdown = input.required<IDropdown>();
  readonly disabled = input<boolean>(false);
  readonly defaultOpen = input<boolean>(true);
  readonly selectedId = input<string | null>(null);
  readonly selected = output<string>();

  readonly isOpen = signal<boolean>(true);
  readonly selectedItem = computed(() =>
    this.dropdown().items.find(item => item.id === this.selectedId()) ?? null,
  );
  readonly displayLabel = computed(() => this.selectedItem()?.label ?? this.dropdown().label);

  ngOnInit(): void {
    this.isOpen.set(this.defaultOpen());
  }

  toggle(): void {
    if (this.disabled()) return;
    this.isOpen.update(isOpen => !isOpen);
  }

  select(item: IDropdownItem): void {
    if (this.disabled()) return;
    this.selected.emit(item.id);
    this.isOpen.set(false);
  }
}
