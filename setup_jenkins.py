import pythoncom, win32api
import time
from win32com.taskscheduler import taskscheduler
import win32com.client
import jenkins


def create_daily_task(name, cmd, hour=None, minute=None):
    """creates a daily task"""
    cmd = cmd.split()
    ts = pythoncom.CoCreateInstance(taskscheduler.CLSID_CTaskScheduler,None,
                                    pythoncom.CLSCTX_INPROC_SERVER,
                                    taskscheduler.IID_ITaskScheduler)

    if '%s.job' % name not in ts.Enum():
        task = ts.NewWorkItem(name)
        task.SetApplicationName(cmd[0])
        task.SetParameters(' '.join(cmd[1:]))
        task.SetPriority(taskscheduler.REALTIME_PRIORITY_CLASS)
        task.SetFlags(taskscheduler.TASK_FLAG_RUN_ONLY_IF_LOGGED_ON)
        task.SetAccountInformation('', None)
        ts.AddWorkItem(name, task)
        run_time = time.localtime(time.time() + 300)
        tr_ind, tr = task.CreateTrigger()
        tt = tr.GetTrigger()
        tt.Flags = 0
        tt.BeginYear = int(time.strftime('%Y', run_time))
        tt.BeginMonth = int(time.strftime('%m', run_time))
        tt.BeginDay = int(time.strftime('%d', run_time))
        if minute is None:
            tt.StartMinute = int(time.strftime('%M', run_time))
        else:
            tt.StartMinute = minute
        if hour is None:
            tt.StartHour = int(time.strftime('%H', run_time))
        else:
            tt.StartHour = hour
        tt.TriggerType = int(taskscheduler.TASK_TIME_TRIGGER_DAILY)
        tr.SetTrigger(tt)
        pf = task.QueryInterface(pythoncom.IID_IPersistFile)
        pf.Save(None,1)
        task.Run()
    else:
        raise KeyError("%s already exists" % name)
    task = ts.Activate(name)
    exit_code, startup_error_code = task.GetExitCode()
    return win32api.FormatMessage(startup_error_code)


computer_name = ""  # leave all blank for current computer, current user
computer_username = ""
computer_userdomain = ""
computer_password = ""
action_id = "connect to jenkins"  # action name
action_path = r"c:\windows\system32\calc.exe"  # executable path (could be python.exe)
action_arguments = r''  # arguments (could be something.py)
action_workdir = r"c:\jenkins"  # working directory for action executable
author = "Jarell Douville"  # so that end users know who you are
description = "testing task"  # so that end users can identify the task
task_id = "jenkins"
username = ""
password = ""

# define constants
TASK_TRIGGER_DAILY = 2
TASK_CREATE = 2
TASK_CREATE_OR_UPDATE = 6
TASK_ACTION_EXEC = 0
# IID_ITask = "{148BD524-A2AB-11CE-B11F-00AA00530503}"


class RunFlags(object):
    TASK_RUN_NO_FLAGS = 0
    TASK_RUN_AS_SELF = 1
    TASK_RUN_IGNORE_CONSTRAINTS = 2
    TASK_RUN_USE_SESSION_ID = 4
    TASK_RUN_USER_SID = 8


# connect to the scheduler (Vista/Server 2008 and above only)
def create_task():
    scheduler = win32com.client.Dispatch("Schedule.Service")
    scheduler.Connect(computer_name or None, computer_username or None, computer_userdomain or None, computer_password or None)
    root_fldr = scheduler.GetFolder("\\")

    # the task
    task = scheduler.NewTask(0)
    task_triggers = task.Triggers
    trigger = task_triggers.Create(TASK_TRIGGER_DAILY)
    trigger.DaysInterval = 100
    trigger.StartBoundary = "2100-01-01T08:00:00-00:00"  # never start
    trigger.Enabled = False

    # the task action
    task_actions = task.Actions
    action = task_actions.Create(TASK_ACTION_EXEC)
    action.ID = action_id
    action.Path = action_path
    action.WorkingDirectory = action_workdir
    action.Arguments = action_arguments
    info = task.RegistrationInfo
    info.Author = author
    info.Description = description
    settings = task.Settings
    settings.Enabled = False
    settings.Hidden = False

    # register task
    result = root_fldr.RegisterTaskDefinition(task_id, task, TASK_CREATE_OR_UPDATE, "", "", RunFlags.TASK_RUN_NO_FLAGS)

    # run the task once
    new_task = root_fldr.GetTask(task_id)
    new_task.Enabled = True
    running_task = new_task.Run("")
    new_task.Enabled = False


jenkins_url = 'http://90tvmcjnkd/jenkins'


def setup_jenkins():
    server = jenkins.Jenkins(jenkins_url, username='a24472', password='')


if __name__ == '__main__':
    create_task()
