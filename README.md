# gh-standardize
A highly customizable Python tool that helps you standardize GitHub repositories.
This is mostly useful for organizations who want to maintain a standardized configuration across all repositories.

**Features:**
- Standardize label names, colors, and descriptions
- Standardize file locations, and contents
    - Load file contents from URL, or local file
- Standardize branch protections
- Repository level configuration for opting out of, or creating custom rules.
- Make standardization changes on a specific branch, with the option to autmatically create a PR to some other branch.

**Requirements:**
- Python 3
- A GitHub API key (either organization or user)
- pipenv

## Config File Schema
**Master Config**

The master config file is required.


```json
{
    "PRHEAD": "",
    "PRBASE": "",
    "AUTOMERGE": false,
    "EXEMPT": {
        "REPOS": ["exempt_repo_name"]
    },
    "TEMPLATES": [
        {
            "name": "FILENAME.extension",
            "localPath": "path/to/file.extension",
            "targetPath": "path/to/"
        },
        ...
    ],
    "PROTECTIONS": ["master"],
    "LABELS": {
        "labelname": {
            "color": "hexcolor",
            "description": "This label means..."
        },
        ...
    }
}
```

**Repository Config**

The repository config is not required. 
Repositories are opted-in for all rules defined in the master config by default. 
The repo config allows you to opt out of standardization entirely, or opt out of specific rules. If no repository config file is found at runtime, all standardization rules will be applied to the repository.

The custom object allows you to create rules at a repository level. For example, the config file below will create a label called "exampleName", with color "ffffff", and description "label description" in that repository only.

```json
{
    "ISEXEMPT": false,
    "IGNORE": {
        "LABELS": [],
        "TEMPLATES": [],
        "BRANCHPROTECTION": []
    },
    "CUSTOM": {
        "LABELS": {
            "exampleName": {
                "color": "ffffff",
                "description": "label description"
            }
        }
    }
}


```