import { ChangeDetectionStrategy, Component, computed, inject } from '@angular/core';

import { Chip } from '@components/chip/chip';
import { ConversationFacade } from '@domain/facades/conversation';

@Component({
  selector: 'talk2db-header',
  imports: [Chip],
  templateUrl: './header.html',
  styleUrl: './header.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class Header {
  private readonly _conversationFacade = inject(ConversationFacade);

  public readonly title = "SQL Assistant";
  public readonly conversationTitle = computed(() => this._conversationFacade.currentConversation()?.title?.trim() ?? '');
  public readonly conversationSchema = computed(() => this._conversationFacade.currentConversation()?.schema_name?.trim() ?? '');
}
