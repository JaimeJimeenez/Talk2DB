import { ChangeDetectionStrategy, Component, input, output } from '@angular/core';

import { Icon } from '@components/icon/icon';
import { ArtifactLink } from '@components/artifact-link/artifact-link';
import { Message, QueryArtifact } from '@domain/models/message';

@Component({
  selector: 'talk2db-answer',
  imports: [Icon, ArtifactLink],
  templateUrl: './answer.html',
  styleUrl: './answer.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class Answer {
  readonly message = input.required<Message>();
  readonly artifactSelected = output<QueryArtifact>();

  readonly botIcon = { name: 'bot', size: 20, title: 'AI Assistant' };
}
