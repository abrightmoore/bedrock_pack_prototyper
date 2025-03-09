#   @TheWorldFoundry
import random
import os
import sys
import glob
import shutil
import time
import math
import pygame
import json

CURRENT_GAME_VER = [1, 21, 62]  #   Todo: Open the game and look at what this number is on the main menu lower right
SCRIPT_SERVER_LIB_VER = "1.16.0"
SCRIPT_UI_LIB_VER = "1.3.0"
PSEP = "\\"

class FileSystem:
    def __init__(self):
        pass

    def write_lines_to_file(self, filename, lines):
        separ = ""
        for line in lines:
            self.write_line_to_file(filename, line, separ)
            if separ == "":
                separ = "\n"

    def write_line_to_file(self, filename, line, separ):
        if separ == None:
            separ = "\n"
        theFile = open(filename, 'a+')
        theFile.write(separ + str(line))
        theFile.close()


    def get_filenames(self, path, pattern):
        print('Scanning available files...')
        fileNames = glob.glob(path+pattern) # E.g. *.png
        return fileNames

    def make_dir(self, path):
        try:
            os.mkdir(path)
        except OSError:
            print ("Creation of the directory %s failed" % path)
        else:
            print ("Successfully created the directory %s " % path)

    def make_path_to_file(self, path):
        parts = path.split(PSEP)
        if (len(parts) == 1):
            parts = path.split("/")
        path_use = ""
        for i in range(0,len(parts)):
            path_use = path_use+parts[i]
            self.make_dir(path_use)
            path_use = path_use+"/"

    def write_json(self, filename, json_object):
        with open(filename, "w") as outfile:
            #outfile.write(json_object)
            json.dump(json_object, outfile, indent=4, sort_keys=True)


    def getUUID(self):
        digits = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "a", "b", "c", "d", "e", "f"]

        result = ""
        for i in xrange(0, 32):
            result += digits[randint(0, len(digits) - 1)]
            if len(result) == 8 or len(result) == 13 or len(result) == 18 or len(result) == 23:
                result += "-"
        return result

    def isDir(self, path):
        return os.path.isdir(path)

class Pack:
    colour_codes = { 
        "black" : "§0",
        "dark_blue" : "§1",
        "dark_green" : "§2",
        "dark_aqua" : "§3",
        "dark_red" : "§4",
        "dark_purple" : "§5",
        "gold" : "§6",
        "gray" : "§7",
        "dark_gray" : "§8",
        "blue" : "§9",
        "green" : "§a",
        "aqua" : "§b",
        "red" : "§c",
        "light_purple" : "§d",
        "yellow" : "§e",
        "white" : "§f"
    }
    format_codes = {
        "Obfuscated" : "§k",
        "Bold" : "§l",
        "Strikethrough" : "§m",
        "Underline" : "§n",
        "Italic" : "§o",
        "Reset" : "§r"
    }
    
    #  Todo: obfuscation/compression of paths
    
    class RP:
        def __init__(self, pack):
            self.pack = pack
            self.id = pack.rp_id

        def write_to_disk(self, path):
            fs = FileSystem()
            rp = {
                "format_version": 2,
                "header": {
                    "description": "pack.description",
                    "min_engine_version": CURRENT_GAME_VER,
                    "name": "pack.name",
                    "uuid": self.id,
                    "version": [1, 0, 0]
                },
                "modules": [
                    {
                        "type": "resources",
                        "uuid": pack.getUUID(),
                        "version": [1, 0, 0]
                    }
                ],
                "dependencies": [
                    {
                        "uuid": self.pack.bp_id,
                        "version": [1, 0, 0]
                    }
                ]
            }            

            fs.make_path_to_file(os.path.join(path, "texts"))
            content_languages = [ "en_US" ]
            self.pack.write_json(os.path.join(os.path.join(path, "texts"),"languages.json"), content_languages)
            content_en_US = [ "pack.name="+pack.project_name, "pack.description="+pack.project_name+" by "+pack.team_name ]
            fs.write_lines_to_file(os.path.join(os.path.join(path, "texts"),"en_US.lang"), content_en_US)
            
            fs.make_path_to_file(os.path.join(path, "textures"+PSEP+self.pack.team_id+PSEP+self.pack.project_id))
            self.pack.write_json(os.path.join(path, "manifest.json"), rp)

        
    class BP:
        def __init__(self, pack):
            self.pack = pack
            self.id = pack.bp_id
            
        def write_to_disk(self, path):
            fs = FileSystem()

            script_main_path = "scripts"+PSEP+self.pack.team_id+PSEP+self.pack.project_id #   Todo: os.path this
            fs.make_path_to_file(os.path.join(path,script_main_path))

            bp = {
                "format_version": 2,
                "header": {
                    "name": "pack.name",
                    "description": "pack.description",
                    "uuid": self.id,
                    "version": [1, 0, 0],
                    "min_engine_version": CURRENT_GAME_VER,
                    "pack_scope": "world"
                },
                "metadata": {
                    "product_type": "addon",
                    "authors": [self.pack.team_name]
                },
                "modules": [
                    {
                        "description": "Behavior",
                        "version": [1, 0, 0],
                        "uuid": self.pack.getUUID(),
                        "type": "data"
                    },
                    {
                        "description": "Scripting",
                        "uuid": self.pack.getUUID(),
                        "version": [1, 0, 0],
                        "type": "script",
                        "language": "javascript",
                        "entry": os.path.join(script_main_path,"main.js").replace("\\","/")
                    },
                    {
                        "type": "data", 
                        "uuid": self.pack.getUUID(), 
                        "version": [1, 0, 0]
                    }                    
                ],
                "dependencies": [
                    {
                        "uuid": self.pack.rp_id,
                        "version": [1, 0, 0]
                    },
                    {
                        "module_name": "@minecraft/server",
                        "version": SCRIPT_SERVER_LIB_VER #   Todo: bump this to current
                    },
                    {
                        "module_name": "@minecraft/server-ui",
                        "version": SCRIPT_UI_LIB_VER #   Todo: bump this to current
                    }
                ]
            }

            self.pack.write_json(os.path.join(path, "manifest.json"), bp)
            fs.make_path_to_file(os.path.join(path, "scripts"))
            content_script_main = [
                "//  "+pack.team_name,
                "import * as mc from \"@minecraft/server\";",
                "import * as mcui from \"@minecraft/server-ui\";",
                "const DEBUG = true",
                "const dimensions = [ mc.world.getDimension(\"overworld\"), mc.world.getDimension(\"nether\"), mc.world.getDimension(\"the_end\") ];",
                "",
                "mc.world.afterEvents.itemUse.subscribe(async (event) => {",
                "    const { source: player, itemStack } = event;",
                "        // YOUR CODE GOES HERE });",
                "    });",
                "",
                "let iteration = 0;",
                "if(iteration%20 == 0) { mc.world.sendMessage(\"Tick \"+String(iteration/20));	};",
                "function run_each_frame() {",
                "    iteration++;",
                "    for(let dimension of dimensions) {",
                "        // YOUR CODE GOES HERE",
                "    };",
                "};",
                "",
                "mc.system.runInterval(() => {",
                "   try {",
                "       run_each_frame();",
                "   } catch(error) {",
                "       if(DEBUG) mc.world.sendMessage(\"["+pack.team_id+"] Error in mc.system.runInterval: \"+String(error)+\" \"+String(error.stack));",
                "   };",
                "}, 1);"
            ]
            fs.write_lines_to_file(os.path.join(os.path.join(path, script_main_path),"main.js"), content_script_main)
            
            fs.make_path_to_file(os.path.join(path, "texts"))
            content_languages = [ "en_US" ]
            self.pack.write_json(os.path.join(os.path.join(path, "texts"),"languages.json"), content_languages)
            content_en_US = [ "pack.name="+pack.project_name, "pack.description="+pack.project_name+" by "+pack.team_name ]
            fs.write_lines_to_file(os.path.join(os.path.join(path, "texts"),"en_US.lang"), content_en_US)
            
            fs.make_path_to_file(os.path.join(path, "dimensions"))
            content_dim = { 
              "format_version": "1.18.0", 
                "minecraft:dimension": { 
                  "description": { 
                    "identifier": "minecraft:overworld" 
                  }, 
                  "components": { 
                    "minecraft:dimension_bounds": { 
                      "min": -512, 
                      "max": 512 
                  }, 
                  "minecraft:generation": { 
                      "generator_type": "void" 
                  } 
                } 
              } 
            }
            self.pack.write_json(os.path.join(os.path.join(path, "dimensions"),"overworld.json"), content_dim)
           
    def __init__(self, team_name, project_name, assets ):
        self.project_name = project_name
        self.team_name = team_name
        self.team_id = self.get_id_from_name(team_name)
        self.project_id = self.get_id_from_name(project_name)
        self.project_namespace = self.team_id + "_" + self.project_id
        self.assets = assets
        self.rp_id = self.getUUID()
        self.bp_id = self.getUUID()
        while (self.bp_id == self.rp_id):   #   Resolve duplicates
            self.bp_id = self.getUUID()
        self.rp = self.RP(self)
        self.bp = self.BP(self)


    def write_to_disk(self, root_path):
        #   Persist the RP and BP and all the stubs that are needed for a coherent MVP
        path = os.path.join(root_path, self.project_namespace)
        self.rp.write_to_disk(os.path.join(path, self.project_namespace+"_r"))
        self.bp.write_to_disk(os.path.join(path, self.project_namespace+"_b"))

        self.log("Pack has been written to disk")
        

    def get_id_from_name(self, name):
        #   Take each first letter of the name and concatenate it as a lower case word
        name_parts = name.split()
        result = ""
        for np in name_parts:
            result = result + np[0]
        
        return result.lower()


    def getUUID(self):
        digits = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "a", "b", "c", "d", "e", "f"]

        result = ""
        for i in range(0, 32):
            result += digits[random.randint(0, len(digits) - 1)]
            if len(result) == 8 or len(result) == 13 or len(result) == 18 or len(result) == 23:
                result += "-"
        return result


    def write_json(self, filename, json_object):
        with open(filename, "w") as outfile:
            json.dump(json_object, outfile, indent=4, sort_keys=True)


    def log(self, message):
        print(message)


pack = Pack("The World Foundry", "ABOUT TIME", None)
print(pack.project_id)
pack.write_to_disk("out")