import type { FormProps } from "antd";
import { Button, Form, Input } from "antd";
import { FC } from "react";
import type { LoginProps } from "../types";

const onFinish: FormProps<LoginProps>["onFinish"] = ({
  email,
  password,
}: LoginProps) => {
  console.table({
    email,
    password,
  });
  window.pywebview.api.store_credentials(email, password);
};

export const Login: FC = () => {
  const [form] = Form.useForm<LoginProps>();

  return (
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
        rules={[{ required: true, message: "Please input your email!" }]}>
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
  );
};
