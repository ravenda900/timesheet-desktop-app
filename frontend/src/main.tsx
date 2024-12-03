import React from "react";
import ReactDOM from "react-dom/client";
import { App } from "./App.tsx";
import "./index.css";
import type { ConfigureFormProps, ProjectIssue } from "./types";

declare global {
  interface Window {
    pywebview: {
      api: {
        has_credentials: () => Promise<boolean>;
        store_credentials: (email: string, password: string) => Promise<void>;
        store_configuration: (config: ConfigureFormProps) => Promise<void>;
        get_configuration: (isApi: boolean) => Promise<ConfigureFormProps>;
        has_configuration: () => Promise<boolean>;
        get_projects: () => Promise<ProjectIssue[]>;
      };
      [key: string]: unknown;
    };
  }
}

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
