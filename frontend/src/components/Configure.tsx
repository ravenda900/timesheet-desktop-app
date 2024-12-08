import { SendOutlined } from "@ant-design/icons";
import type { FormProps } from "antd";
import {
  Badge,
  Button,
  Checkbox,
  Divider,
  Form,
  Input,
  List,
  notification,
  Segmented,
  Select,
  Space,
  Spin,
  Tabs,
  TimePicker,
  Tooltip,
  Typography,
} from "antd";
import dayjs from "dayjs";
import {
  FC,
  MouseEventHandler,
  useCallback,
  useEffect,
  useMemo,
  useState,
} from "react";
import type { AntdFormValue, ProjectIssue } from "../types";
import { Mode } from "../types/enums";
import { VALIDATION_MESSAGES } from "../utils/constants";

const format = "HH:mm";

export const Configure: FC = () => {
  const [form] = Form.useForm<AntdFormValue>();
  const [isConfigLoaded, setIsConfigLoaded] = useState<boolean>();
  const [api, contextHolder] = notification.useNotification();
  const [projectIssueOptions, setProjectIssueOptions] =
    useState<ProjectIssue[]>();
  const mode = Form.useWatch("mode", form);
  const [missingEntries, setMissingEntries] = useState<string[]>();

  const onFinish: FormProps<AntdFormValue>["onFinish"] =
    useCallback(async () => {
      try {
        await window.pywebview.api.create_timesheet();
        api.open({
          type: "success",
          message: "Success",
          description: "Timesheet created successfully.",
          showProgress: true,
          pauseOnHover: true,
        });
      } catch (e) {
        api.open({
          type: "error",
          message: "Error",
          description: "Failed to create timesheet.",
          duration: 0,
        });
      }
    }, [api]);

  const onSaveConfig = useCallback<MouseEventHandler<HTMLElement>>(() => {
    (async () => {
      try {
        const values = await form.validateFields();
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
    })();
  }, [api, form]);

  const onCreateMissingEntries = useCallback<
    MouseEventHandler<HTMLElement>
  >(() => {
    (async () => {
      try {
        await window.pywebview.api.create_missing_entries();
        api.open({
          type: "success",
          message: "Success",
          description: "Missing entries has been filled.",
          showProgress: true,
          pauseOnHover: true,
        });
      } catch (e) {
        api.open({
          type: "error",
          message: "Error",
          description: "Failed to fill missing entries.",
          duration: 0,
        });
      }
    })();
  }, [api]);

  const onCreateMissingEntry = useCallback(
    (date: string) => {
      (async () => {
        try {
          await window.pywebview.api.create_missing_entry(date);
          api.open({
            type: "success",
            message: "Success",
            description: `Missing entry for ${date} has been created`,
            showProgress: true,
            pauseOnHover: true,
          });
        } catch (e) {
          api.open({
            type: "error",
            message: "Error",
            description: `Failed to fill missing entry for ${date}.`,
            duration: 0,
          });
        }
      })();
    },
    [api],
  );

  useEffect(() => {
    const handlePywebviewReady = () => {
      if (!window.pywebview.state) {
        window.pywebview.state = {};
      }

      window.pywebview.state.setProjectIssueOptions = setProjectIssueOptions;
      window.pywebview.state.setMissingEntries = setMissingEntries;
    };

    if (window.pywebview) {
      handlePywebviewReady();
    } else {
      window.addEventListener("pywebviewready", handlePywebviewReady);
    }

    return () => {
      window.removeEventListener("pywebviewready", handlePywebviewReady);
    };
  }, [api]);

  const isLoaded = useMemo(
    () => typeof projectIssueOptions !== "undefined" && isConfigLoaded,
    [projectIssueOptions, isConfigLoaded],
  );

  useEffect(() => {
    (async () => {
      if (isLoaded) {
        return;
      }
      const hasConfig = await window.pywebview.api.has_configuration();
      if (hasConfig) {
        const config = await window.pywebview.api.get_configuration(true);

        form.setFieldsValue({
          ...config,
          scheduledTime: dayjs(config.scheduledTime, format),
          time: [dayjs(config.time[0], format), dayjs(config.time[1], format)],
          breakTime: dayjs(config.breakTime, format),
        });
      } else {
        form.resetFields();
      }
      setIsConfigLoaded(true);
    })();
  }, [form, isLoaded]);

  const missingEntriesContent = useMemo(
    () => (
      <>
        <List
          size="small"
          dataSource={missingEntries}
          renderItem={(item) => (
            <List.Item
              actions={[
                <Tooltip title="Create timesheet entry for this date">
                  <Button
                    color="primary"
                    variant="link"
                    onClick={() => onCreateMissingEntry(item)}
                    icon={<SendOutlined />}
                  />
                </Tooltip>,
              ]}>
              No timesheet entry found in {item}
            </List.Item>
          )}
        />
        <Tooltip
          title={
            <>
              Creates missing timesheet entries using saved configuration in
              <em>config.ini</em>
            </>
          }>
          <Button
            color="primary"
            htmlType="button"
            variant="solid"
            className="mt-5 mx-auto"
            onClick={onCreateMissingEntries}
            block>
            Create missing entries
          </Button>
        </Tooltip>
      </>
    ),
    [missingEntries, onCreateMissingEntries, onCreateMissingEntry],
  );

  const configureContent = useMemo(
    () => (
      <Spin spinning={!isLoaded}>
        <Form
          form={form}
          colon={false}
          variant="filled"
          labelCol={{ span: 6 }}
          wrapperCol={{ span: 16 }}
          layout="horizontal"
          className="max-w-xl"
          onFinish={onFinish}
          validateMessages={VALIDATION_MESSAGES}
          initialValues={{
            mode: Mode.AUTOMATIC,
            time: [dayjs("10:00", format), dayjs("19:00", format)],
            breakTime: dayjs("00:00", format),
            endNextDay: false,
            comment: "",
          }}>
          <Form.Item label="Mode" name="mode" rules={[{ required: true }]}>
            <Segmented options={Object.values(Mode)} />
          </Form.Item>

          <Divider />
          <Form.Item
            label="Scheduled Time"
            name="scheduledTime"
            rules={[{ required: true }]}
            extra="The time when the automated creation of timesheet will trigger (Automatic) or when the dialog will show up (Manual)">
            <TimePicker format={format} />
          </Form.Item>
          <Divider />

          <Form.Item
            label="Time"
            name="time"
            className="mb-0"
            rules={[{ required: true }]}>
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

          <Form.Item
            label="Break"
            name="breakTime"
            rules={[{ required: true }]}>
            <TimePicker minuteStep={5} format={format} />
          </Form.Item>

          <Form.Item label="Comment" name="comment">
            <Input.TextArea placeholder="Enter comment here..." />
          </Form.Item>

          <Form.Item
            label="Project"
            name="project"
            extra="The project where the all the work hours will be spent"
            tooltip="Only one project is supported currently"
            rules={[{ required: true }]}>
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
            <Space>
              {mode === Mode.MANUAL && (
                <Tooltip
                  title={`Creates timesheet entry today: ${dayjs().format("YYYY-MM-DD")}`}>
                  <Button color="primary" variant="solid" htmlType="submit">
                    Create
                  </Button>
                </Tooltip>
              )}
              <Tooltip
                title={
                  <>
                    Saves configuration in <em>config.ini</em>
                  </>
                }>
                <Button
                  color="primary"
                  htmlType="button"
                  variant="outlined"
                  onClick={onSaveConfig}>
                  Save
                </Button>
              </Tooltip>
            </Space>
          </Form.Item>
        </Form>
        {isLoaded && (
          <Typography.Paragraph className="mt-5">
            Configuration from <em>config.ini</em> was successfully loaded
          </Typography.Paragraph>
        )}
      </Spin>
    ),
    [form, isLoaded, mode, onFinish, onSaveConfig, projectIssueOptions],
  );

  const contentWithTabs = useMemo(() => {
    if (typeof missingEntries !== "undefined") {
      return (
        <Tabs
          items={[
            {
              label: "General",
              key: "general",
              children: configureContent,
            },
            {
              label: (
                <Space>
                  Missing Entries
                  <Badge size="small" count={missingEntries?.length} />
                </Space>
              ),
              key: "missingEntries",
              children: missingEntriesContent,
            },
          ]}
        />
      );
    }

    return configureContent;
  }, [configureContent, missingEntries, missingEntriesContent]);

  return (
    <>
      {contextHolder}
      {contentWithTabs}
    </>
  );
};
