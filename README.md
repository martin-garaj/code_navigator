# Code-navigator

A small HTML/JS/css (and Python) utility to transform .yaml files into 
iteractive hyperlinked document that is viewed locally in a browser.

The **main focus** of Code-navigator is to abadon the *linear* scrolling through documents and replace it by interlinked exploration, where the reader naturally browses the documents/pages/sections/phrases/words/symbols of interest.

----

This is what is what a hyperlinked document created by Code-navigator looks like.
It consists of 2 side-by-side pages. On the left, documents are viewved in their interactive from. On the right, hyper-linked documents are displayed on-hover, on-click, the document opens on the left side.

![code-navigator-ui](/docs/images/ui.png "Code-navigaort UI")


Documents created by Code-navigator include the following features:

**A**) Breadcrumbs for efficient navigation \
**B**) Markdown parser by default \
**C**) Section headers with external links \
**D**) Highlighting & hyper-linking of key-words \
**E**) Interactive navigation \
**F**) Syntax highlight provided by Pygments \
**G**) Proper line-numbering on line-wrapping \
**H**) Image insertion (_not displayed_) 

![code-navigator-ui-explained](/docs/images/ui_marked.png "Code-navigaort UI explained")


# How to view documents

1) clone this repo ```git clone https://github.com/martin-garaj/code_navigator.git```
2) go to the root folder (where `config.yaml` is found) and start python server ```python3 -m http.server 8000```
3) open browser and go to ```localhost:8000``` and browse the document



# How to generate documents

1) clone this repo ```git clone https://github.com/martin-garaj/code_navigator.git```
2) navigate to ```<repo root>/data_to_explore```
3) create a bunch of .yaml files based on this template below
4) run `python generate_html.py -r -f -v` to (re)generate .yaml files in .html
5) console output will accompany you to correct any irregularities


```yaml
header:                                             # compulsory
    title: intro                                    # compulsory
    titlePrefix:                                    # optional
    permalink:                                      # optional
sections:                                           # optional
    - sectionTag: <section name>                    # compulsory
        header:                                     # optional
            title: <section title>                  # optional
            titlePrefix: <title prefix, e.g. /src/>    # optional
            permalink: <e.g. gihut permalink>       # optional
        links:                                      # optional
            - matchString: <work to be linked>      # compulsory
                linkFile: <filename.yaml to be linked to>       # compulsory
                matchIndex: <[]-link all, [0, 1, 2] - link 1,2,3 occurance, [-1] - link everything but the first occurance>    # compulsory
                sectionTag: <sectionTag to scroll to>     # optional
                cssClass: <additional CSS class, e.g. for different color highlight>       # optional
        content:
            lineNumberStart: int                    # optional, otherwise get #Lxxx from permalink, default 1
            syntaxHighlight: <see Pygments docs>    # optional (default config.syntaxHighlight)
            text: |                                 # optional
                code to be highlighted and displayed

    - sectionTag: <section name showing image>      # compulsory
        image:                                      # optional
            path: <path to image file>              # compulsory
            altText: <alternative text>             # optional
            maxWidth: <CSS property, e.g. 50%>      # optional, default 100 or 'auto' (if height is defined)
            maxHeight: <CSS property, e.g. 50%>     # optional, default 'auto'
```

