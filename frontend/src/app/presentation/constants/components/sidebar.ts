import { IButton } from "@interfaces/components/button";
import { ISidebar } from "@interfaces/components/sidebar";

export const SIDEBAR_ITEMS: ISidebar[] = [
  {
    icon: "history",
    label: "Consultas recientes",
    path: "/history",
  },
  {
    icon: "database",
    label: "Esquemas de bases de datos",
    path: "/schema",
  },
  {
    icon: "chart-line",
    label: "Métrica de uso",
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
