import { Dayjs } from "dayjs";

export type ConfigureFormProps = {
  mode: string;
  scheduledTime?: string;
  project: string;
  time: [string, string];
  endNextDay: boolean;
  breakTime: string;
  comment: string;
};

export type AntdFormValue = Omit<
  ConfigureFormProps,
  "time" | "breakTime" | "scheduledTime"
> & {
  scheduledTime?: Dayjs;
  time: [Dayjs, Dayjs];
  breakTime: Dayjs;
};

export type LoginProps = {
  email: string;
  password: string;
};

export type User = {
  key: string;
  url: string;
  icon: string;
  username: string;
  displayname: string;
};

export type Group = {
  id: number;
  name: string;
  description: string;
  memberCount: number;
};

export type ProjectIssue = {
  id: number;
  key: string;
  summary: string;
  url: string;
  icon: string;
  issueType: string;
  issueTypeDesc: string;
  status: string;
  statusHTML: string;
  projectStartDate: string;
  projectEndDate: string;
  isBookable: boolean;
  isProject: boolean;
  isSubProject: boolean;
  isWorkPackage: boolean;
  timesheetAssignedUsers: User[];
  timesheetAssignedGroups: Group[];
  workpackages: unknown[];
};
