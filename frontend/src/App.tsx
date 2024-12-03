import { useEffect, useMemo, useState } from "react";
import { Login } from "./components/Login";
import { Divider, Spin, Typography } from "antd";
import { Configure } from "./components/Configure";

export const App = () => {
  const [hasCredentials, setHasCredentials] = useState<boolean>();

  useEffect(() => {
    (async () => {
      setHasCredentials(await window.pywebview.api.has_credentials());
    })();
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
      <Divider />
      <div className="mt-3">{content}</div>
    </div>
  );
};
