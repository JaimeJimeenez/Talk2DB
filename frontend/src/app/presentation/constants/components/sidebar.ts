import { IButton } from "@interfaces/components/button";
import { ISidebar } from "@interfaces/components/sidebar";

export const SIDEBAR_ITEMS: ISidebar[] = [
  {
    icon: "timer",
    label: "Recent queries",
    path: "/history",
  },
  {
    icon: "database",
    label: "Database schema",
    path: "/schema",
  },
  {
    icon: "chart-line",
    label: "Usage metrics",
    path: "/metrics",
  }
];

export const NEW_CHAT_BUTTON: IButton = {
  label: "New chat",
  startIcon: {
    name: "plus",
    title: "New chat",
    size: 16,
  },
  class: "new_chat-button",
  disabled: false,
  onClick: () => { },
  type: 'button'
};