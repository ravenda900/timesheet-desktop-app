import type { FormProps } from "antd";
import {
  Button,
  Checkbox,
  Divider,
  Form,
  Input,
  notification,
  Segmented,
  Select,
  TimePicker,
  Typography,
} from "antd";
import dayjs from "dayjs";
import { FC, useCallback, useEffect, useState } from "react";
import { ProjectIssue, type AntdFormValue } from "../types";

const format = "HH:mm";

export const Configure: FC = () => {
  const [form] = Form.useForm<AntdFormValue>();
  const [isConfigLoaded, setIsConfigLoaded] = useState(false);
  const [api, contextHolder] = notification.useNotification();
  const [projectIssueOptions, setProjectIssueOptions] =
    useState<ProjectIssue[]>();
  const mode = Form.useWatch("mode", form);

  const onFinish: FormProps<AntdFormValue>["onFinish"] = useCallback(
    async (values: AntdFormValue) => {
      try {
        await window.pywebview.api.store_configuration({
          ...values,
          ...{
            time: [
              values.time[0].format(format),
              values.time[1].format(format),
            ],
            breakTime: values.breakTime.format(format),
            scheduledTime: values.scheduledTime?.format(format),
          },
        });
        api.open({
          type: "success",
          message: "Success",
          description: "Configuration saved successfully.",
          showProgress: true,
          pauseOnHover: true,
        });
      } catch (e) {
        api.open({
          type: "error",
          message: "Error",
          description: "Failed to save configuration.",
          duration: 0,
        });
      }
    },
    [api],
  );

  useEffect(() => {
    (async () => {
      try {
        setProjectIssueOptions(await window.pywebview.api.get_projects());
      } catch (e) {
        api.open({
          type: "error",
          message: "Error",
          description: "Failed to retrieve project issues.",
          duration: 0,
        });
      }
    })();
  }, [api]);

  useEffect(() => {
    (async () => {
      const hasConfig = await window.pywebview.api.has_configuration();

      if (hasConfig) {
        const config = await window.pywebview.api.get_configuration(true);

        form.setFieldsValue({
          ...config,
          scheduledTime: dayjs(config.scheduledTime, format),
          time: [dayjs(config.time[0], format), dayjs(config.time[1], format)],
          breakTime: dayjs(config.breakTime, format),
        });
        setIsConfigLoaded(true);
      }
    })();
  }, [form]);

  return (
    <>
      {contextHolder}
      <Form
        form={form}
        colon={false}
        variant="filled"
        labelCol={{ span: 6 }}
        wrapperCol={{ span: 16 }}
        layout="horizontal"
        className="max-w-xl"
        onFinish={onFinish}
        initialValues={{
          mode: "Automatic",
          time: [dayjs("07:00", format), dayjs("15:00", "HH:mm")],
          breakTime: dayjs("00:00", format),
          endNextDay: false,
          comment: "",
        }}>
        <Form.Item
          label="Mode"
          name="mode"
          extra="Selecting Automatic will create a timesheet entry based on the scheduled time">
          <Segmented options={["Automatic", "Manual"]} />
        </Form.Item>

        {mode === "Automatic" && (
          <>
            <Divider />
            <Form.Item label="Scheduled Time" name="scheduledTime">
              <TimePicker format={format} />
            </Form.Item>
            <Divider />
          </>
        )}

        <Form.Item label="Time" name="time" className="mb-0">
          <TimePicker.RangePicker format={format} />
        </Form.Item>

        <Form.Item
          labelCol={{ span: 0 }}
          wrapperCol={{ offset: 11 }}
          valuePropName="checked"
          name="endNextDay"
          className="scale-75">
          <Checkbox>Ends in the next day</Checkbox>
        </Form.Item>

        <Form.Item label="Break" name="breakTime">
          <TimePicker minuteStep={5} format={format} />
        </Form.Item>

        <Form.Item label="Comment" name="comment">
          <Input.TextArea placeholder="Enter comment here..." />
        </Form.Item>

        <Form.Item
          label="Project"
          name="project"
          extra="Project selected will be the only project that has timesheet entry from start to end">
          <Select
            showSearch
            placeholder="Select a project"
            options={projectIssueOptions?.map((option) => ({
              label: option.summary,
              value: `${option.id}`,
            }))}
          />
        </Form.Item>

        <Form.Item label={null}>
          <Button type="primary" htmlType="submit">
            Submit
          </Button>
        </Form.Item>
      </Form>
      {isConfigLoaded && (
        <Typography.Paragraph className="mt-5" italic>
          Configuration from config.ini was successfully loaded
        </Typography.Paragraph>
      )}
    </>
  );
};
