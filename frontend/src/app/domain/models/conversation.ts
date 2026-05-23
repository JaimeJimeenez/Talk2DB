import { Message } from "./message";

export interface Conversation {
    readonly id: string;
    readonly title: string;
    readonly messages: Message[];
    readonly createdAt: Date;
    readonly schema_id: string;
}
