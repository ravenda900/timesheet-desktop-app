import { Spin, Typography } from "antd";
import { FC, useEffect, useMemo, useState } from "react";
import { Configure } from "./components/Configure";
import { Login } from "./components/Login";

export const App: FC = () => {
  const [hasCredentials, setHasCredentials] = useState<boolean>();

  useEffect(() => {
    const handlePywebviewReady = () => {
      if (!window.pywebview.state) {
        window.pywebview.state = {};
      }

      window.pywebview.state.setHasCredentials = setHasCredentials;
    };

    if (window.pywebview) {
      handlePywebviewReady();
    } else {
      window.addEventListener("pywebviewready", handlePywebviewReady);
    }

    return () => {
      window.removeEventListener("pywebviewready", handlePywebviewReady);
    };
  }, []);

  const content = useMemo(() => {
    if (typeof hasCredentials === "undefined") {
      return <Spin fullscreen></Spin>;
    }
    return hasCredentials ? <Configure /> : <Login />;
  }, [hasCredentials]);

  return (
    <div className="p-5">
      <Typography.Title level={3}>Timesheet Desktop App</Typography.Title>
      <div className="mt-3">{content}</div>
    </div>
  );
};
