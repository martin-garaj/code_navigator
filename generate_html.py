from pathlib import Path


from python_lib.log import print_report, log_set_prepend, log_reset_prepend, \
    print_headline, print_notice, _NOTE, _ERROR, _CRITICAL
from python_lib.check_structure import DataStructureChecker
from python_lib.to_html import StructToHtml
from python_lib.utils import get_files_of_type, load_yaml_file


## ========================================================================== ##
##                                    MAIN                                    ##
## ========================================================================== ##
def main():
    from python_lib.cli import CommandLineInterface

    # console output
    print_headline(headline='CLI INPUTS', fill='-')

    # get command line arguments
    cli = CommandLineInterface(root_path=str(Path(__file__).parent))
    print(f"working directory    : {cli.directory}")
    print(f"force rewrite        : {cli.force}")
    print(f"verbose report       : {cli.verbose}")
    print(f"recursive processing : {cli.recursive}")
    print(f"config-file path     : {cli.config_path}")
    if cli.verbose:
        print(f"config-file content  : {cli.config}")

    # locate all files 
    file_paths = get_files_of_type(
        folder_path=Path(cli.directory, cli.config.display.pathData), 
        file_extension=cli.config.generate.sourceFileExtension, 
        recursive=cli.recursive)
    
    # loop through files
    num_generated = 0
    num_skipped = 0
    for file_idx, file_path in enumerate(file_paths):
        log_set_prepend(value=file_idx+1, max_len=len(str(len(file_paths))))
        
        # show progress
        print_headline(
            headline=\
                f"{file_idx+1}) Processing file '.../{Path(file_path).name}'", 
            fill="=")
        print_report(
            importance=_NOTE, 
            message=f"full path: '{str(file_path)}' ")

        # load data
        data = load_yaml_file(file_path)
        
        # detect deviations of the data structure from reference structure
        file_checker = DataStructureChecker(
                data=data, 
                reference=cli.config.dataStructure, 
            )
        file_checker.print_log(min_importance=_NOTE if cli.verbose else _ERROR)

        # get struct_to_html generator
        struct_to_html = StructToHtml(
                data=data, 
                config=cli.config, 
                root_path=str(Path(__file__).parent),
                suffix=cli.config.generate.targetFileExtension,
            )
        struct_to_html.generate_html_page()
        struct_to_html.print_log(
            min_importance=_NOTE if cli.verbose else _ERROR)

        # save html file
        html_path = \
            Path(file_path)\
                .with_suffix('')\
                .with_suffix(cli.config.generate.targetFileExtension)
                
        if not struct_to_html.valid:
            log_reset_prepend()
            print_notice(notice="SKIP: cannot generate HTML", fill='!')
            num_skipped += 1
        elif html_path.exists() and not cli.force:
            print_report(
                importance=_CRITICAL, 
                message=f"file '{str(html_path)}' already exists! "\
                f"Run this script again with -f/--force option to rewrite "\
                f"existing files.")
            log_reset_prepend()
            print_notice(notice="SKIP: HTML already exists", fill='!')
            num_skipped += 1
        else:
            with open(html_path, "w") as file:
                file.write(struct_to_html.html_page)
            log_reset_prepend()
            print_notice(notice="SUCCESS", fill='~')
            num_generated += 1

        # delete objects
        del file_checker
        del struct_to_html
    
    # summarize script
    log_reset_prepend()
    print_headline(
            headline=f'Generated {num_generated} files (skipped {num_skipped})',
            fill='#', 
            width=80,
        )
    
    
if __name__ == "__main__":
    main()
