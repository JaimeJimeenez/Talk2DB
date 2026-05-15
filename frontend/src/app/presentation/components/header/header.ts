import { ChangeDetectionStrategy, Component } from '@angular/core';

@Component({
  selector: 'talk2db-header',
  imports: [],
  templateUrl: './header.html',
  styleUrl: './header.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class Header {
  public readonly title = "SQL Assistant";
}
