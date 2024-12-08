import React from "react";
import ReactDOM from "react-dom/client";
import { App } from "./App.tsx";
import "./index.css";
import type { ConfigureFormProps, JiraUser } from "./types";

declare global {
  interface Window {
    pywebview: {
      api: {
        store_credentials: (email: string, password: string) => Promise<void>;
        store_configuration: (config: ConfigureFormProps) => Promise<void>;
        get_configuration: (isApi: boolean) => Promise<ConfigureFormProps>;
        has_configuration: () => Promise<boolean>;
        get_myself: (email: string, password: string) => Promise<JiraUser>;
        create_timesheet: () => Promise<void>;
        create_missing_entries: () => Promise<void>;
        create_missing_entry: (date: string) => Promise<void>;
        get_missing_entries: () => Promise<string[]>;
      };
      state: {
        [key: string]: unknown;
      };
    };
  }
}

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
