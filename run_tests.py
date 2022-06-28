from __future__ import print_function
from __future__ import with_statement

import datetime
import os
import shutil
import subprocess
import sys

import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from enum import Enum

from robot import pythonpathsetter
from robot import rebot
from robot import run

# from lib.py import common
from lib.py.gui import center

try:
    from robot.testdoc import TestSuiteFactory
except ImportError as e:
    # tkMessageBox.showerror('Error', 'Robot Framework is not installed!')
    sys.exit(1)


# todo  include suite or test name in results folder

regions = ['QA', 'UAT2', 'DEV2', 'BAU']
default_pythonpath = os.path.join(os.getcwd(), 'lib')


def get_auts():
    root = TestSuiteFactory(os.path.join(os.getcwd(), 'test'))
    return [aut.name for aut in root.suites]


def get_tests_in_suite(suite):
    tests = ['Test_Suite1','Test_Suite2']
    # _get_tests(suite, tests)
    return tests


def _get_tests(suite, tests):
    for test in suite.tests:
        tests.append(test.name)
    for suite_ in suite.suites:
        _get_tests(suite_, tests)


class Browser(Enum):
    FIREFOX = 'firefox'
    CHROME = 'chrome'
    INTERNET_EXPLORER = 'ie'
    EDGE = 'edge'
    SAFARI = 'safari'
    OPERA = 'opera'


def _api_run_test(datasources, serial, test, browser='chrome'):
    print('test: {}'.format(test))
    print('pythonpath: {}'.format(default_pythonpath))
    print('datasources: {}'.format(datasources))
    fldr = './results/{}/tests/{}'.format(serial, test)
    run(
        datasources,
        test=test,
        variable=[
            'browser:{}'.format(browser),
            'region:QA',
            'remote_url:http://90tvmcjnkd:4444/wd/hub'
        ],
        outputdir=fldr
    )
    return test


class Runner(object):

    def __init__(self, aut='', test='', suite='', include='', exclude='', outputdir='', region='QA', browsers=None):
        self.aut = aut
        self.test = test

        self.include = include
        self.exclude = exclude
        self.suite = suite
        self.outputdir = outputdir
        self.region = region
        self.pythonpath = default_pythonpath
        self.keep_console_open = 1
        self.browsers = set(browsers) if browsers else set()
        self.on_remote = 0
        # self.processes = []

    def add_browser(self, browser):
        self.browsers.add(browser)

    def get_run_configurations(self):
        configs = []

        for browser in self.browsers:
            lbl = self.suite if self.suite else self.test
            fldr = '--'.join([self.aut.lower(), lbl.lower(), browser.value, datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S')])
            # cmd = 'pybot.bat'
            cmd = 'robot'
            cmd += ' --variable browser:"{}"'.format(browser.value)
            cmd += ' --variable region:"{}"'.format(self.region)
            if self.on_remote:
                cmd += ' --variable remote_url:http://90tvmcjnkd:4444/wd/hub'
          
            if self.include and self.exclude:
                  cmd += ' --include "{}"'.format(self.include) +  ' --exclude "{}"'.format(self.exclude)
            elif self.include:
                 cmd += ' --include "{}"'.format(self.include)
            elif self.exclude:
                 cmd += ' --exclude "{}"'.format(self.exclude)
            else:
                cmd += ' --test "{}"'.format(self.test)
            

            if self.suite:
                cmd += ' --suite "{}"'.format(self.suite)
            cmd += ' --outputdir "{}"'.format(os.path.join(self.outputdir, fldr))
            cmd += ' --pythonpath "{}"'.format(self.pythonpath)
            cmd += ' test/' + self.aut.lower()
            configs.append(cmd)

        return configs

    def start_sequential(self):
        sel_path = os.path.join(os.getcwd(), 'resources')
        env = os.environ.copy()
        env['PATH'] = sel_path + ';' + env['PATH']

        configs = self.get_run_configurations()
        keep_open = 'k' if self.keep_console_open else 'c'
        for config in configs:
            print('new process: {}'.format(config))
            subprocess.Popen('cmd /{} {}'.format(keep_open, config), cwd=os.getcwd(),
                             creationflags=subprocess.CREATE_NEW_CONSOLE, env=env)


class RunnerGui(tk.Tk):

    def __init__(self):
        tk.Tk.__init__(self)
        self.runner = Runner()

        # Comboboxes
        self.aut_combo = None
        self.browser_combo = None
        self.region_combo = None
        self.test_suite_combo = None

        # Text
        self.cmd_text = None

        self.test_tree = None

        # StringVars
        self.test_suite_choice_sv = None
        self.test_suite_sv = None
        self.include_tags_sv = None
        self.exclude_tags_sv = None
        self.output_dir_sv = None

        self.run_configs = []

        self.initialize()

        self.aut_combo.event_generate('<<ComboboxSelected>>', when='tail')
        self.region_combo.event_generate('<<ComboboxSelected>>', when='tail')

    def initialize(self):
        self.title('Run Tests')

        center(self, 1000, 700)

        root = tk.PanedWindow(self, orient=tk.HORIZONTAL, sashpad=4, sashrelief=tk.RAISED)

        # tests frame
        # ====

        left_frm = tk.Frame(root)

        # aut combobox
        self.aut_combo = ttk.Combobox(left_frm, state='readonly')
        self.aut_combo['values'] = get_auts()
        self.aut_combo.bind('<<ComboboxSelected>>', self.on_aut_selected)
        self.aut_combo.current(0)
        self.aut_combo.grid(row=0, column=0, sticky='ew', padx=5, pady=5)

        # test tree frame
        tf = tk.Frame(left_frm)
        self.test_tree = ttk.Treeview(tf, selectmode='browse')
        ysb = ttk.Scrollbar(tf, orient='vertical', command=self.test_tree.yview)
        self.test_tree.configure(yscroll=ysb.set)
        self.test_tree.heading('#0', text='Tests', anchor='center')
        self.test_tree.bind('<<TreeviewSelect>>', self.on_test_suite_selected)
        self.test_tree.grid(row=0, column=0, sticky='nsew')
        ysb.grid(row=0, column=1, sticky='ns')
        tf.rowconfigure(0, weight=1)
        tf.columnconfigure(0, weight=1)
        tf.grid(row=1, column=0, sticky='nsew', padx=5, pady=5)

        # filter
        # self.test_filter = tk.StringVar()
        # test_filter_edit = tk.Entry(left_frm, textvariable=self.test_filter)
        # test_filter_edit.grid(row=2, column=0, columnspan=2, sticky='ew', padx=5, pady=5)
        # self.test_filter.trace('w', self.on_test_filter_changed)

        left_frm.rowconfigure(1, weight=1)
        left_frm.columnconfigure(0, weight=1)
        root.add(left_frm)

        right_frm = tk.Frame(root)

        self.region_combo = ttk.Combobox(right_frm, state='readonly')
        self.region_combo['values'] = regions
        self.region_combo.bind('<<ComboboxSelected>>', self.on_region_selected)
        self.region_combo.current(0)
        self.region_combo.grid(row=0, column=0, columnspan=2, sticky='ew', padx=5, pady=5)

        incl_lbl = tk.Label(right_frm, text='Include Tags:')
        incl_lbl.grid(row=1, column=0, pady=(20, 5), sticky='e')
        self.include_tags_sv = tk.StringVar()
        self.include_tags_sv.trace('w', self.on_include_tags_changed)
        include_tags_entry = tk.Entry(right_frm, textvariable=self.include_tags_sv)
        include_tags_entry.grid(row=1, column=1, sticky='ew', padx=5, pady=(20, 5))

        exclude_lbl = tk.Label(right_frm, text='Exclude Tags:')
        exclude_lbl.grid(row=2, column=0, pady=(5, 20), sticky='e')
        self.exclude_tags_sv = tk.StringVar()
        self.exclude_tags_sv.trace('w', self.on_exclude_tags_changed)
        exclude_tags_entry = tk.Entry(right_frm, textvariable=self.exclude_tags_sv)
        exclude_tags_entry.grid(row=2, column=1, sticky='ew', padx=5, pady=(5, 20))

        browsers_lbl = tk.Label(right_frm, text='Browsers:')
        browsers_lbl.grid(row=3, column=0, sticky='e', padx=5, pady=0)
        self.chrome_iv = tk.IntVar()
        self.chrome_iv.trace('w', lambda *args: self.on_browser_selection_changed(Browser.CHROME))
        chrome_chkbut = tk.Checkbutton(right_frm, text='Chrome', variable=self.chrome_iv)
        chrome_chkbut.grid(row=3, column=1, sticky='w', padx=5, pady=0)
        self.internetexplorer_iv = tk.IntVar()
        self.internetexplorer_iv.trace('w', lambda *args: self.on_browser_selection_changed(Browser.INTERNET_EXPLORER))
        internetexplorer_chkbut = tk.Checkbutton(right_frm, text='Internet Explorer', variable=self.internetexplorer_iv)
        internetexplorer_chkbut.grid(row=4, column=1, sticky='w', padx=5, pady=0)
        self.firefox_iv = tk.IntVar()
        self.firefox_iv.trace('w', lambda *args: self.on_browser_selection_changed(Browser.FIREFOX))
        firefox_chkbut = tk.Checkbutton(right_frm, text='Firefox', variable=self.firefox_iv)
        firefox_chkbut.grid(row=5, column=1, sticky='w', padx=5, pady=0)

        output_lbl = tk.Label(right_frm, text='Results:')
        output_lbl.grid(row=6, column=0, padx=5, pady=(10, 30), sticky='e')
        self.output_dir_sv = tk.StringVar()
        output_dir = tk.Button(right_frm, textvariable=self.output_dir_sv, command=self.set_output_dir)
        self.output_dir_sv.trace('w', self.on_output_dir_changed)
        output_dir.grid(row=6, column=1, sticky='ew', padx=5, pady=(10, 30))

        remote_frm = tk.LabelFrame(right_frm, text='Remote')
        # use remote machines
        self.on_remote_machines_iv = tk.IntVar()
        self.on_remote_machines_iv.set(0)
        on_remote_machines_chkbtn = tk.Checkbutton(remote_frm, text='Run in Grid', variable=self.on_remote_machines_iv)

        def change_on_remote(*args):
            self.runner.on_remote = self.on_remote_machines_iv.get()
            self.update_cmd_display()

        self.on_remote_machines_iv.trace('w', change_on_remote)
        on_remote_machines_chkbtn.grid(row=0, column=0, sticky='w', padx=5, pady=5)
        # run in parallel
        self.remote_parallel_iv = tk.IntVar()
        self.remote_parallel_iv.set(0)
        remote_parallel_chkbtn = tk.Checkbutton(remote_frm, text='Run in Parallel', variable=self.remote_parallel_iv)

        def change_in_parallel(*args):
            self.runner.in_parallel = self.remote_parallel_iv.get()
            self.update_cmd_display()

        self.remote_parallel_iv.trace('w', change_in_parallel)
        remote_parallel_chkbtn.grid(row=0, column=1, sticky='w', padx=5, pady=5)

        remote_frm.grid(row=7, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')

        self.cmd_text_frm = tk.LabelFrame(right_frm, text='Run Configurations')
        pad = tk.Label(self.cmd_text_frm)
        pad.grid(row=0, column=0)
        self.cmd_text_frm.columnconfigure(0, weight=1)
        self.cmd_text_frm.grid(row=8, column=0, columnspan=2, padx=5, pady=5, sticky='nsew')

        # keep console window open
        self.keep_console_open_iv = tk.IntVar()
        self.keep_console_open_iv.set(1)
        keep_console_open_chkbut = tk.Checkbutton(right_frm, text='Keep Console(s) Open', variable=self.keep_console_open_iv)

        def change_keep_console_open(*args):
            self.runner.keep_console_open = self.keep_console_open_iv.get()
            self.update_cmd_display()

        self.keep_console_open_iv.trace('w', change_keep_console_open)
        keep_console_open_chkbut.grid(row=9, column=0, sticky='w', padx=5, pady=5)

        # start button
        self.run_btn = tk.Button(right_frm, text='Run', command=self.on_run_btn_clicked, state='disabled')
        self.run_btn.grid(row=9, column=1, sticky='ew', padx=5, pady=5)

        # tests frame
        # ====
        right_frm.columnconfigure(1, weight=1)
        right_frm.rowconfigure(8, weight=1)

        root.add(right_frm)
        root.paneconfigure(left_frm, minsize=400)
        root.paneconfigure(right_frm, minsize=400)
        root.pack(fill=tk.BOTH, expand=True)

        self.output_dir_sv.set('./results')
        # self.test_suite_choice_sv.set('test')

    def on_run_btn_clicked(self, event=None):
        if self.remote_parallel_iv.get():
            self.runner.start_parallel()
        else:
            self.runner.start_sequential()

    def on_browser_selection_changed(self, browser):
        if browser == Browser.FIREFOX:
            value = self.firefox_iv.get()
        elif browser == Browser.CHROME:
            value = self.chrome_iv.get()
        elif browser == Browser.INTERNET_EXPLORER:
            value = self.internetexplorer_iv.get()
        else:
            raise Exception
        if value:
            self.runner.browsers.add(browser)
        else:
            self.runner.browsers.remove(browser)
        self.update_cmd_display()

    def update_cmd_display(self):
        for config in self.run_configs:
            config.grid_remove()

        self.run_configs = []

        configs = self.runner.get_run_configurations()
        for idx, config in enumerate(configs):
            config_text = tk.Text(self.cmd_text_frm, height=3)
            config_text.grid(row=idx+1, column=0, sticky='new', padx=5, pady=5)
            # config_text.delete('1.0', tk.END)
            config_text.insert('1.0', config)
            self.run_configs.append(config_text)

        if configs:
            self.run_btn.config(state='normal')
        else:
            self.run_btn.config(state='disabled')

    def set_output_dir(self, event=None):
        filename = filedialog.askdirectory()
        if not filename:
            return
        self.output_dir_sv.set(filename)

    def on_output_dir_changed(self, *args):
        self.runner.outputdir = self.output_dir_sv.get()

    def on_aut_selected(self, event=None):
        self.runner.aut = self.aut_combo.get()
        self.refresh_tests()
        self.update_cmd_display()

    def on_region_selected(self, event=None):
        self.runner.region = self.region_combo.get()
        self.update_cmd_display()

    def on_include_tags_changed(self, *args):
        self.runner.include = self.include_tags_sv.get()
        self.update_cmd_display()

    def on_exclude_tags_changed(self, *args):
        self.runner.exclude = self.exclude_tags_sv.get()
        self.update_cmd_display()

    def refresh_tests(self, event=None):
        aut = self.aut_combo.get()
        suite = TestSuiteFactory(os.path.join('test', aut))
        for i in self.test_tree.get_children():
            self.test_tree.delete(i)
        self.walk_tests(self.test_tree, suite, '')

    def walk_tests(self, tv, suite, parent):
        parent = tv.insert(parent, 'end', text=suite.name, open=True)
        for t in suite.tests:
            tv.insert(parent, 'end', text=t.name, open=True)
        for p in suite.suites:
            self.walk_tests(tv, p, parent)

    def on_test_suite_selected(self, event=None):
        idx = self.test_tree.selection()
        if not idx:
            return
        if self.test_tree.get_children(idx):
            self.runner.test = ''
            self.runner.suite = self.test_tree.item(idx)['text']
        else:
            self.runner.test = self.test_tree.item(idx)['text']
            self.runner.suite = ''
        self.update_cmd_display()


if __name__ == '__main__':
    if len(sys.argv) > 2:
        aut = sys.argv[1]
        suite = sys.argv[2]
        runner = Runner(aut=aut, suite=suite, outputdir='test')
        # runner.start_parallel()
    else:
        gui = RunnerGui()
        gui.mainloop()

    # a = SRunner('mybranch', include=['sit'])
    # a.run()
