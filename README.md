# code-navigator

A small HTML/JS/css (and Python) utility to transform .yaml files into 
iteractive hyperlinked document that runs locally.

# how to view documents

1) clone this repo ```git clone https://github.com/martin-garaj/code_navigator.git```
2) go to the root and start python server ```python3 -m http.server 8000```
3) open browser and go to ```localhost:8000``` and browse the documents

# how to generate documents

1) clone this repo ```git clone https://github.com/martin-garaj/code_navigator.git```
2) navigate to ```<repo root>/data_to_explore```
3) create a bunch of yaml files based on this template:

```yaml
header:
    title: intro
    titlePrefix: 
    permalink: 

sections:
    - sectionTag: <name of the section>
        header: 
            title: Introduction
            titlePrefix: 
            permalink: 
            sectionTag:
            cssClass:
            content:
        syntaxHighlight: markdown
        text: |
            text to be displayed

    - sectionTag: code
        header: 
            title: simple.cpp
            titlePrefix: /path/to/file/within/codebased
            permalink: <permanent link, e.g. to github>
        links:
            - matchString: <string to be matched where link will be displayed>
              linkFile: <relative path>/<file>.yaml
              matchIndex: []
              sectionTag:
              cssClass:
        content:
            syntaxHighlight: cpp
            text: |
                code to be highlighted and displayed
```

# llama.cpp

- get hash by running ```git rev-parse --verify HEAD``` or short ```git rev-parse --short HEAD```
hash: acb2c32c336ce60d765bb189563cc216e57e9fc2
hash (short): acb2c32c

# repo version based on SHA

```console
git fetch origin
git reset --hard acb2c32c336ce60d765bb189563cc216e57e9fc2
```

