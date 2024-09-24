import argparse
import json
import os
from pathlib import Path
import sys
from types import SimpleNamespace
import yaml


from python_lib.log import print_report, _CRITICAL


## ========================================================================== ##
##                            CommandLineInterface                            ##
## ========================================================================== ##
class CommandLineInterface():

    def __init__(self, root_path:str):
        self.root_path = root_path
        self.parser = self._register_parser(root_path=root_path)
        self._process_config_arguments(root_path=root_path)


    # read only properties
    @property
    def force(self):
        return self._force
    @property
    def verbose(self):
        return self._verbose
    @property
    def recursive(self):
        return self._recursive
    @property
    def directory(self):
        return self._directory
    @property
    def config(self):
        return self._config
    @property
    def config_path(self):
        return self._config_path


    def _register_parser(self, root_path:str):
        parser = argparse.ArgumentParser(
            description=\
                f"Processes all <file_name>.yaml in process_path="\
                f"<this-script-path>/<config.display.pathData>/ into HTML files "\
                f"(<file_name>.yaml are kept untouched).")
        parser.add_argument("-d", "--directory", 
                    default=str(Path(root_path)),
                    help=f"Path to directory where the script will "\
                        f"execute (default: script's directory)")
        parser.add_argument("-r", "--recursive", 
                    action="store_true",
                    help=f"If set, the script enters all sub-folders.")
        parser.add_argument("-f", "--force", 
                    action="store_true",
                    help=f"If set, existing files will be replaced by "\
                        f"newly generated files")
        parser.add_argument("-c", "--config", 
                    default=str(Path(root_path).joinpath("config.yaml")),
                    help=f"Path to config file "\
                        f"(default: config.yaml in script's directory)")
        parser.add_argument("-v", "--verbose", 
                    action="store_true",
                    help=f"If set, the script produces verbose output.")
        
        return parser


    def _process_config_arguments(self, root_path:str):
        args = self.parser.parse_args()
        # Process config argument
        if os.path.isabs(args.config):
            config_path = Path(args.config)
        else:
            config_path = Path(Path(root_path).joinpath(args.config))
        if not config_path.exists():
            print_report(
                importance=_CRITICAL, 
                message=f"The specified config file does not exist: "\
                        f"{config_path}")
            sys.exit(1)
        else:
            try:
                def load_object(dct):
                    return SimpleNamespace(**dct)
                with open(config_path, 'r') as file:
                    config_dict = yaml.safe_load(file)
                    config = json.loads(json.dumps(config_dict), 
                                        object_hook=load_object)
                    config.dataStructure = config_dict['dataStructure']
            except Exception as e:
                print_report(
                    importance=_CRITICAL, 
                    message=f"The specified config file cannot be parsed: {e}")
                sys.exit(1)

        # Process directory argument
        if os.path.isabs(args.directory):
            if not os.path.exists(args.directory):
                print_report(
                    importance=_CRITICAL, 
                    message=\
                        f"The specified directory does not exist: "\
                        f"{args.directory}")
                sys.exit(1)
            directory = Path(args.directory)
        else:
            directory = Path(Path(__file__).joinpath(args.directory))
            if not directory.exists():
                print_report(
                    importance=_CRITICAL, 
                    message=\
                        f"The specified relative directory does not exist: "\
                        f"{directory}")
                sys.exit(1)

        # set members
        self._verbose = args.verbose
        self._force = args.force
        self._recursive = args.recursive
        self._directory = directory
        self._config = config
        self._config_path = config_path