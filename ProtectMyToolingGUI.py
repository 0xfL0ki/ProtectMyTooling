#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Author:
#   Mariusz Banach / mgeeky, '20-'22
#   <mb [at] binary-offensive.com>
#   (https://github.com/mgeeky)
#

import time
import os, sys

from lib.utils import *
from lib.logger import Logger
from lib.packersloader import PackersLoader
import lib.optionsparser

import PySimpleGUI as sg



# https://stackoverflow.com/a/69064884
def runCommand(cmd, timeout=None, window=None):
    
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    output = ''

    for line in p.stdout:
        line = line.decode(errors='replace' if (sys.version_info) < (3, 5) else 'ignore').rstrip()
        output += line
        print(line)
        window.Refresh() if window else None

    retval = p.wait(timeout)
    return (retval, output)                         

def run(command, width = 120):
    font = ("Consolas", 10)
    sg.theme("Dark")

    layout = [
        [
            sg.Text("ProtectMyTooling output:", font=font),
        ],
        [
            sg.Multiline(size=(width, 60), font=font, echo_stdout_stderr=False, reroute_stdout=True, reroute_stderr=True, no_scrollbar=False, horizontal_scroll=True)
        ],
        [
            sg.Button("Close", key="-Exit-", font=font),
        ],
    ]

    window = sg.Window("Protection in progres...", layout, modal=True, finalize=True)
    runCommand(cmd=command, window=window)
  
    while True:
        event, values = window.read()
        if event == "-Exit-" or event == sg.WIN_CLOSED:
            break

    window.close()

def showConfig(config):
    font = ("Consolas", 10)
    sg.theme("Dark")

    layout = [
        [
            sg.Text(config, font=font),
        ],
        [
            sg.Multiline(size=(120, 60), font=font, echo_stdout_stderr=False, reroute_stdout=True, reroute_stderr=True)
        ],
        [
            sg.Button("Close", key="-Exit-", font=font),
        ],
    ]

    window = sg.Window("Protection in progres...", layout, modal=True, finalize=True)
    
    with open(config) as f:
        print(f.read())
  
    while True:
        event, values = window.read()
        if event == "-Exit-" or event == sg.WIN_CLOSED:
            break

    window.close()

def createWindow(packersChain, packersList):
    font = ("Consolas", 10)
    font2 = ("Consolas", 11)
    sg.theme("Dark")

    tooltip1 = 'Inject watermark to generated artifact. Syntax: where=value, example: "-w dos-stub=Foobar". Available watermark places: dos-stub,checksum,overlay,section . Section requires NAME,STR syntax where NAME denotes PE section name, e.g. "-w section=.foo,bar" will create PE section named ".foo" with contents "bar". May be repeated'
    tooltip2 = 'Specify a custom IOC value that is to be written into output IOCs csv file in column "comment"'

    params_column = [
        [
            sg.Text("Input File" + ' ' * 7, font=font ),
            sg.Input(size=(50, 1), enable_events=True, key="-infile-", font=font),
            sg.FileBrowse(font=font),
        ],
        [
            sg.Text("File Architecture" , font=font),
            sg.Combo(size=(10, 1), values=["Auto", "x86", "x64"], readonly=True, default_value="Auto", enable_events=True, key="-arch-", font=font),
        ],
        [
            sg.Text("Output Folder" + ' ' * 4, font=font),
            sg.Input(size=(50, 1), enable_events=True, key="-outdir-", font=font),
            sg.FolderBrowse(font=font),
        ],
        [
            sg.Text("Output File name" + ' ' * 1, font=font),
            sg.Input(size=(50, 1), enable_events=True, key="-outfilename-", font=font),
        ],
        [
            sg.Text("Packers chain:", font=font2),
        ],
        [
            sg.Column([
                [
                    sg.Listbox(values=packersChain, enable_events=True, size=(25, 15), pad=(5,5), key="-packers chain-", font=font2),
                ]
            ]),
            sg.Column([
                [sg.Button("Move Up", font=font),],
                [sg.Button("Move Down", font=font),],
                [sg.Button("Remove", font=font),],
                [sg.Button("Clear", font=font),],
            ]),
  
        ],
        [
            sg.Text("", font=font),
            #sg.HSeparator(),
        ],
        [
            sg.Text("Config path", font=font),
            sg.Input(size=(56, 1), default_text=os.path.abspath(os.path.join(os.path.dirname(__file__), "config/ProtectMyTooling.yaml")), enable_events=True, key="-config-", font=font),
            sg.FileBrowse(font=font),
        ],
        [
            sg.Text("Watermark" + ' ' * 2, font=font, tooltip=tooltip1),
            sg.Input(size=(65, 1), default_text="section=.foo,1234567890abcdef123456", pad=(5,5), enable_events=True, key="-watermark-", font=font, tooltip=tooltip1),
        ],
        [
            sg.Text("Custom IOC" + ' ' * 1, font=font, tooltip=tooltip2),
            sg.Input(size=(65, 1), default_text="", pad=(5,5), enable_events=True, key="-customioc-", font=font, tooltip=tooltip2),
        ],
        [
            sg.Checkbox('Collect IOCs', default=False, tooltip="Collect IOCs and save them to .csv file side by side to <outfile>", font=font),
            sg.Checkbox('Hide Console', default=False, tooltip="If output artifact is PE EXE, use this option to hide Console window by switching PE Subsystem from WINDOWS_GUI", font=font),
            sg.Checkbox('Verbose', default=True, font=font),
            sg.Checkbox('Debug', default=False, font=font)
        ]
    ]

    packers_column = [
        [
            sg.Text("Choose packers to work with:", font=font),
        ],
        [
            sg.Listbox(values=packersList, enable_events=True, size=(20, 30), pad=(5,5), key="-packers available-", font=font),
        ],
        [
            sg.Button("Add to chain", font=font),
        ]
    ]

    layout = [
        [
            sg.Column(params_column),
            sg.VSeparator(),
            sg.Column(packers_column),
        ],
        [
            sg.HSeparator(),
        ],
        [
            sg.Text("", key='-current chain-', font=font2),
        ],
        [
            sg.Text("", font=font),
        ],
        [
            sg.Button("Protect", tooltip = "Runs ProtectMyTooling.py with provided arguments.", font=font),
            sg.Button("Protect & Run", tooltip = "Protects input payload and runs protected file without parameters.", font=font),
            sg.Button("List Packers & Details", tooltip = "List all packers details.", font=font),
            sg.Button("Show Config", tooltip = "Preview configuration YAML contents.", font=font),
        ]
    ]

    window = sg.Window("ProtectMyTooling", layout, return_keyboard_events=True)
    return window

def main():
    packersList = []
    packersChain = []

    files = os.listdir(os.path.join(os.path.dirname('__file__'), 'packers'))

    for f in files:
        if f.lower().endswith('.py'):
            name = os.path.basename(f).replace('.py', '')

            if name.lower() not in ['__init__', 'ipacker']:
                packersList.append(name)

    window = createWindow(packersChain, packersList)

    while True:
        event, values = window.read()
        if event == "Exit" or event == sg.WIN_CLOSED:
            break

        elif event == "Add to chain":
            packersChain.append(values['-packers available-'])
            chain = f'"{os.path.basename(values["-infile-"])}"'
            for p in packersChain:
                chain = f"{p[0].capitalize()}({chain})"
                
            window['-current chain-'].update(chain)
            window["-packers chain-"].update(packersChain)

            chain = f'"{os.path.basename(values["-infile-"])}"'
            for p in packersChain:
                chain = f"{p[0].capitalize()}({chain})"

            window['-current chain-'].update(chain)

        elif event == "Remove":    
            index = int(''.join(map(str, window["-packers chain-"].get_indexes())))
            packersChain.pop(index)
            
            chain = f'"{os.path.basename(values["-infile-"])}"'
            for p in packersChain:
                chain = f"{p[0].capitalize()}({chain})"
                
            window['-current chain-'].update(chain) 
            window["-packers chain-"].update(packersChain, set_to_index=[index - 1], scroll_to_index=index - 1)

        elif event == "Clear":
            packersChain.clear()
            window['-current chain-'].update("")
            window["-packers chain-"].update(packersChain)
        
        elif event == "List Packers & Details":
            script = os.path.abspath(os.path.join(os.path.dirname(__file__), 'ProtectMyTooling.py'))

            with tempfile.NamedTemporaryFile() as temp:
                logpath = temp.name + ".log"
                command = [
                    sys.executable,
                    script,
                    '-L',
                    '--widest-packers-list'
                ]

                run(command, width = 200)
            
        elif event == "Move Up":
            index = int(''.join(map(str, window["-packers chain-"].get_indexes())))
            
            if index > 0:
                packersChain.insert(index - 1, packersChain.pop(index))
                window["-packers chain-"].update(packersChain, set_to_index=[index - 1], scroll_to_index=index - 1)

                chain = f'"{os.path.basename(values["-infile-"])}"'
                for p in packersChain:
                    chain = f"{p[0].capitalize()}({chain})"
                window['-current chain-'].update(chain) 

        elif event == "Move Down":    
            index = int(''.join(map(str, window["-packers chain-"].get_indexes())))

            if index + 1 < len(packersChain):
                packersChain.insert(index + 1, packersChain.pop(index))
                window["-packers chain-"].update(packersChain, set_to_index=[index + 1], scroll_to_index=index + 1)

                chain = f'"{os.path.basename(values["-infile-"])}"'
                for p in packersChain:
                    chain = f"{p[0].capitalize()}({chain})"
                window['-current chain-'].update(chain) 

        elif event == "-infile-":
            p = os.path.normpath(os.path.abspath(values["-infile-"]))
            path, ext = os.path.splitext(p)
            newname = os.path.basename(path) + '-obf' + ext
            window["-outfilename-"].update(os.path.basename(newname))
            window["-infile-"].update(p)

            if len(values["-outdir-"]) == 0:
                window["-outdir-"].update(os.path.dirname(p))

        elif event == "Show Config":
            if len(values["-config-"]) > 0:
                showConfig(values["-config-"])

        elif 'Up' in event or '16777235' in event:
            element = window.find_element_with_focus().Key

            if element in ['-packers chain-', '-packers available-']:
                cur_index = window.Element(element).Widget.curselection()
                cur_index = (cur_index[0] - 1) % window.Element(element).Widget.size()
                window.Element(element).Update(set_to_index=cur_index)
                window.Element(element).Update(scroll_to_index=cur_index)
                window.write_event_value(element, [window.Element(element).GetListValues()[cur_index]])

        elif 'Down' in event or '16777237' in event:
            element = window.find_element_with_focus().Key

            if element in ['-packers chain-', '-packers available-']:
                cur_index = window.Element(element).Widget.curselection()
                cur_index = (cur_index[0] + 1) % window.Element(element).Widget.size()
                window.Element(element).Update(set_to_index=cur_index)
                window.Element(element).Update(scroll_to_index=cur_index)
                window.write_event_value(element, [window.Element(element).GetListValues()[cur_index]])

        elif event == "Protect" or event == "Protect & Run":
            infile = os.path.normpath(os.path.abspath(values["-infile-"]))
            arch = values["-arch-"]
            watermark = values["-watermark-"]
            config = values["-config-"]
            customioc = values["-customioc-"]
            outfile = os.path.normpath(os.path.abspath(os.path.join(values["-outdir-"], values["-outfilename-"])))
            packers = ','.join([x[0] for x in packersChain])

            with tempfile.NamedTemporaryFile() as temp:
                logpath = temp.name + ".log"

                script = os.path.abspath(os.path.join(os.path.dirname(__file__), 'ProtectMyTooling.py'))

                command = [
                    sys.executable,
                    script,
                    '-c',
                    config,
                    packers,
                    '-l',
                    logpath,
                    '-C',
                    '--arch',
                    arch,
                    infile,
                    outfile
                ]

                if len(watermark) > 0: command.extend(['-w', watermark])
                if len(customioc) > 0: command.extend(['-I', customioc])

                if values['Collect IOCs']: command.append('-i')
                if values['Hide Console']: command.append('-g')
                if values['Verbose']: command.append('-v')
                if values['Debug']: command.append('-d')

                if event == "Protect & Run": command.append('-r')

                if os.path.isfile(outfile):
                    os.remove(outfile)

                run(command, logpath)

    window.close()

if __name__ == '__main__':
    main()
