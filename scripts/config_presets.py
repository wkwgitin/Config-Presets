# Config Presets script for Automatic1111
# Version: 0.1
# Release date: TBD
# Author: Zyin

import modules.scripts as scripts
import gradio as gr
import ast
import os
import platform
import subprocess as sp


ui_seed = None                   #"seed" component in ui.py:283, label='Seed'
ui_steps = None                  #"steps" component in ui.py:635, label='Sampling Steps'
ui_sampler_index = None          #"steps" component in ui.py:636, label='Sampling method'
ui_width = None                  #"width" component in ui.py:639, label='Width'
ui_height = None                 #"height" component in ui.py:640, label='Width'
ui_enable_hr = None              #"enable_hr" component in ui.py:645,label='Highres. fix'
ui_denoising_strength = None     #"denoising_strength" component in ui.py:650, label='Denoising strength'
ui_batch_count = None            #"batch_count" component in ui.py:653, label='Batch count'
ui_batch_size = None             #"batch_size" component in ui.py:654, label='Batch size'
ui_cfg_scale = None              #"cfg_scale" component in ui.py:656, label='CFG Scale'
component_count = 0

# Load config from file
config_presets = {}
try:
    with open("scripts/config_presets.json") as file:
        config_presets = ast.literal_eval(file.read())
except:
    print("[ERROR] config_presets.py: Could not find config file 'scripts/config_presets.json'. Did you forget to move the file along with config_presets.py when installing this script?.")



class Script(scripts.Script):
    def title(self):
        return "Config Presets"

    def show(self, is_img2img):
        return True#not is_img2img #only show in txt2img

    def after_component(self, component, **kwargs):
        global ui_steps
        global ui_sampler_index
        global ui_width
        global ui_height
        global ui_enable_hr
        global ui_denoising_strength
        global ui_batch_count
        global ui_batch_size
        global ui_cfg_scale

        global component_count
        component_count += 1

        #print(f"after_component() {component_count}: {type(component)}")

        # Since we can't get direct access to component variables in ui.py, we detect and save a reference to them here.
        if isinstance(component, gr.components.Number):
            if component.label == "Seed":
                ui_seed = component
                #print(f"found ui_seed component: {type(component)}")
        elif isinstance(component, gr.components.Slider):
            if component.label == "Sampling Steps":
                ui_steps = component
                #print(f"found ui_steps component: {type(component)}")
            elif component.label == "Width":
                ui_width = component
                #print(f"found ui_width component: {type(component)}")
            elif component.label == "Height":
                ui_height = component
                #print(f"found ui_height component: {type(component)}")
            elif component.label == "Denoising strength":
                ui_denoising_strength = component
                #print(f"found ui_denoising_strength component: {type(component)}")
            elif component.label == "Batch count":
                ui_batch_count = component
                #print(f"found ui_batch_count component: {type(component)}")
            elif component.label == "Batch size":
                ui_batch_size = component
                #print(f"found ui_batch_size component: {type(component)}")
            elif component.label == "CFG Scale":
                ui_cfg_scale = component
                #print(f"found ui_cfg_scale component: {type(component)}")
        elif isinstance(component, gr.components.Checkbox):
            if component.label == "Highres. fix":
                ui_enable_hr = component
                #print(f"found ui_enable_hr component: {type(component)}")
        elif isinstance(component, gr.components.Radio):
            if component.label == "Sampling method":
                ui_sampler_index = component
                #print(f"found ui_sampler_index component: {type(component)}")


        if component.elem_id == "open_folder": #bottom of the image gallery
        #if component.elem_id == "script_list": #bottom of the script dropdown
        #if component.elem_id == "txt2img_style2_index": #doesn't work, need to be added after all the components we edit are loaded
            global config_presets
            preset_values = []
            for k in config_presets:
                preset_values.append(k)
                #print(f"Config Presets: added \"{k}\"")

            with gr.Column():
                def config_preset_dropdown_change(value):
                    global config_presets
                    config_dict = config_presets[value]
                    #print(f"config key,values={config_dict}")
                    print(f"Config Presets: changed to {value}")

                    #BUG: tried to get the Highres. fix subrow to display on change, but doesn't work
                    #ui_enable_hr.update(value=True)
                    #ui_enable_hr.change(True)

                    return config_dict["steps"] if "steps" in config_dict else ui_steps.value,\
                           config_dict["sampler_index"] if "sampler_index" in config_dict else ui_sampler_index.value,\
                           config_dict["width"] if "width" in config_dict else ui_width.value,\
                           config_dict["height"] if "height" in config_dict else ui_height.value,\
                           config_dict["enable_hr"] if "enable_hr" in config_dict else ui_enable_hr.value,\
                           config_dict["denoising_strength"] if "denoising_strength" in config_dict else ui_denoising_strength.value,\
                           config_dict["batch_count"] if "batch_count" in config_dict else ui_batch_count.value,\
                           config_dict["batch_size"] if "batch_size" in config_dict else ui_batch_size.value,\
                           config_dict["cfg_scale"] if "cfg_scale" in config_dict else ui_cfg_scale.value,\

                config_preset_dropdown = gr.Dropdown(label="Config Presets", choices=preset_values, elem_id="config_preset_dropdown")
                config_preset_dropdown.style(container=False) #set to True to give it a white box to sit in
                config_preset_dropdown.change(config_preset_dropdown_change, show_progress=False, inputs=[config_preset_dropdown], outputs=[ui_steps, ui_sampler_index, ui_width, ui_height, ui_enable_hr, ui_denoising_strength, ui_batch_count, ui_batch_size, ui_cfg_scale])

                config_preset_dropdown.change(None, inputs=[], outputs=[], _js="""
                    function() {
                        //there is a race condition between the checkbox being checked in Python, and us firing its change event in JavaScript, so wait a bit before firing the event
                         setTimeout(function() { 
                            //the "Highres. fix" checkbox has no easy way to identify it, so use its tooltip attribute on the neighboring element
                            let highresCheckbox = gradioApp().querySelector("label > span[title='Use a two step process to partially create an image at smaller resolution, upscale, and then improve details in it without changing composition'").parentElement.firstChild
                            
                            var event = document.createEvent("HTMLEvents")
                            event.initEvent("change", true, false)
                            highresCheckbox.dispatchEvent(event)
                        }, 200) //50ms is too fast
                        
                    }
                """)



    def ui(self, is_img2img):
        with gr.Row(variant="panel"):

            def open_file(f):
                path = os.path.normpath(os.getcwd() + "\\" + f)

                if not os.path.exists(path):
                    print(f'Config Presets: File "{path}" does not exist. It can be downloaded from this scripts GitHub.')
                    return

                # copied from ui.py:538
                if platform.system() == "Windows":
                    os.startfile(path)
                elif platform.system() == "Darwin":
                    sp.Popen(["open", path])
                else:
                    sp.Popen(["xdg-open", path])


            open_config_file_button = gr.Button(value="\U0001f4c2 Open scripts/config_presets.json", elem_id="open_config_file_button")
            open_config_file_button.click(
                fn=lambda: open_file("scripts\\" + "config_presets.json"),
                inputs=[],
                outputs=[],
            )
            
        with gr.Row():

            gr.HTML(
                """
                <style type="text/css">
                    .configpresets-list {
                        list-style-type:disc;
                        margin-left:3em;
                    }
                    .configpresets-section {
                        margin-left: 20px;
                    }
                </style>
                
                <div class="configpresets-section">
                    <br>This is not a runnable script. This script just adds the "Config Presets" dropdown under the image gallery.
                    <br>
                    <br>The presets in the dropdown can be changed in the <code>scripts/config_presets.json</code> file. Removing a value from a preset will cause that value to be set to the default value as defined in ui-config.json. To apply any changes, go to the Settings tab and click the "Restart Gradio and Refresh Components" button.
                    <br>
                    <br>The following values are accepted in <code>config_presets.json</code>:
                    <ul class="configpresets-list">
                        <li>steps</li>
                        <li>sampler_index (sample name, as seen in the UI)</li>
                        <li>width</li>
                        <li>height</li>
                        <li>enable_hr (this is Highres. fix, True or False)</li>
                        <li>denoising_strength</li>
                        <li>batch_count</li>
                        <li>batch_size</li>
                        <li>cfg_scale</li>
                    </ul>
                    <br>This script only works with English localization.
                </div>
                """)
        return []

    def run(self, p):
        return #generate images as if this script isn't activated