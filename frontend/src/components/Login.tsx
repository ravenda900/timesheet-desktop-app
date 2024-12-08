import type { FormProps } from "antd";
import { Button, Form, Input, notification } from "antd";
import { FC, useCallback } from "react";
import type { LoginProps } from "../types";

export const Login: FC = () => {
  const [form] = Form.useForm<LoginProps>();
  const [api, contextHolder] = notification.useNotification();

  const isValidAccount = useCallback(
    async (email: string, password: string) => {
      try {
        const user = await window.pywebview.api.get_myself(email, password);

        if (!user) {
          throw new Error("Invalid credentials.");
        }
        return !!user;
      } catch (e) {
        if (e instanceof Error) {
          api.open({
            type: "error",
            message: "Error",
            description: e.message,
          });
        }
        console.error("Unknown error occured", e);
      }
      return false;
    },
    [api],
  );

  const onFinish: FormProps<LoginProps>["onFinish"] = useCallback(
    async ({ email, password }: LoginProps) => {
      const isValid = await isValidAccount(email, password);
      console.log("isValid", isValid);
      if (isValid) {
        window.pywebview.api.store_credentials(email, password);
      }
    },
    [isValidAccount],
  );

  return (
    <>
      {contextHolder}
      <Form
        form={form}
        colon={false}
        variant="filled"
        labelCol={{ span: 4 }}
        wrapperCol={{ span: 14 }}
        layout="horizontal"
        className="max-w-xl"
        onFinish={onFinish}
        autoComplete="off">
        <Form.Item
          label="Email"
          name="email"
          rules={[
            {
              required: true,
              type: "email",
              message: "Please input your email!",
            },
          ]}>
          <Input />
        </Form.Item>

        <Form.Item
          label="Password"
          name="password"
          rules={[{ required: true, message: "Please input your password!" }]}>
          <Input.Password />
        </Form.Item>

        <Form.Item label={null}>
          <Button type="primary" htmlType="submit">
            Login
          </Button>
        </Form.Item>
      </Form>
    </>
  );
};
