import json
import os
import zipfile
import pip
import sys

class Poster():
    def __init__(self, build_json) -> None:
        self.init()
        self.read_post(build_json)
        try:
            self.project_config = json.load(open(self.project_name + ".json", 'r', encoding='utf-8'))
            self.module_list = self.project_config["module_list"]
        except FileNotFoundError:
            self.project_config = {}
            self.module_list = []
        try:
            if sys.argv[1] == "mkbasedir":
                self.make_base_dir()
            elif sys.argv[1] == "build":
                self.build()
            elif sys.argv[1] == "download-module":
                self.download_all_module()
            elif sys.argv[1] == "run":
                self.run_self()
            elif "." in sys.argv[1]:
                run(sys.argv[1])
        except IndexError:
            pass

    def init(self, package = "com.example", project_name = "poster", project_version = "0.0.1-a", main_file = "__main__.py", init_package = "__init__.py") -> None:
        self.project_name = project_name.lower()
        self.package = package.lower()
        self.project_version = project_version
        self.main_file = main_file
        self.init_package_file = init_package
        self.start_config = []
        self.config = json.load(open(".poster/poster_config.json", 'r', encoding='utf-8'))

    def read_post(self, post_file):
        post = json.load(open(post_file, "r", encoding='utf-8'))
        post: dict
        for key, value in post.items():
            if key == "name":
                self.project_name = value
            elif key == "version":
                self.project_version = value
            elif key == "package":
                self.package = value
            elif key == "main":
                self.main_file = value
            elif key == "init":
                self.init_package_file = value
            elif key == "libraries":
                self.module_list = value
            elif key == "start_config":
                self.start_config = value
            else:
                pass

    def add_module(self, module: dict[str, str]):
        try:
            module["name"]
            module["version"]
        except IndexError:
            raise ValueError("模块不合规")
        if self.project_config == {}:
            raise ValueError("你不可以这样做")
        if module not in self.module_list: 
            self.module_list.append(module)
            self.project_config["module_list"] = self.module_list
        with open(self.project_name + ".json", 'w', encoding='utf-8') as f:
            json.dump(self.project_config, f)
    
    def download_all_module(self):
        for i in self.module_list:
            print("正在下载", i["name"] + ":" + i["version"])
            pip.main(["install", "--target", os.getcwd() + "/src/main/python/org/pypi/", "-i", "https://pypi.doubanio.com/simple", "{name}=={version}".format(name=i["name"], version=i["version"])])
    
    def make_base_dir(self):
        try:
            os.makedirs("src/main/python")
            os.makedirs("src/main/resources")
            open(self.project_name + ".json", "x", encoding='utf-8').write('{"name": "' + self.project_name + '", "version": "' + self.project_version + '", "package": "' + self.package + "." + self.project_name + '", "main": "' + self.main_file + '", "init": "' + self.init_package_file + '", "module_list": []}')
            os.makedirs("src/main/python/" + str(self.package + "/" + self.project_name).replace(".", "/"))
            open("src/main/python/" + str(self.package + "/" + self.project_name).replace(".", "/") + "/" + self.init_package_file, "x", encoding='utf-8').write("from . import *\n")
            open("src/main/python/" + str(self.package + "/" + self.project_name).replace(".", "/") + "/" + self.main_file, "x", encoding='utf-8').close()
        except:
            raise ValueError("文件已存在")

    def build(self):
        build_post = zipfile.ZipFile(self.project_name + " " + self.project_version + ".post", "w")
        def forEach(dirs):
            for i in os.listdir(dirs):
                if os.path.isfile(dirs + "/" + i):
                    build_post.write(dirs + "/" + i)
                else:
                    forEach(dirs + "/" + i)

        forEach("src")
        open(".main", "x", encoding='utf-8').write("src/main/python/" + str(self.package + "/" + self.project_name).replace(".", "/") + "/" + self.main_file)
        build_post.write(".main")
        build_post.close()
        os.remove(".main")

    def run_self(self):
        sys.path.append(os.getcwd() + "/src/main/python")
        exec(compile(open("src/main/python/" + str(self.package + "/" + self.project_name).replace(".", "/") + "/" + self.main_file, "r", encoding='utf-8').read(), "", "exec"))

def run(file):
    post = zipfile.ZipFile(file)
    post.extractall("./.tmp/")
    post.close()
    del post
    sys.path.append(os.getcwd() + "/.tmp/src/main/python")
    exec(compile(open(".tmp/" + open("./.tmp/.main", 'r', encoding='utf-8').read(), "r", encoding='utf-8').read(), "", "exec"))
    os.popen("rm -rf ./.tmp")

poster = Poster("build.json")