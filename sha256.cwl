cwlVersion: v1.0
class: CommandLineTool
baseCommand: sha256sum
inputs:
    filename:
        type: File
        inputBinding:
            position: 1
outputs:
    hash:
        type: string
        outputBinding:
            glob: ${
                    var arr = inputs.filename.path.split("/");
                    var outpath = arr[arr.length - 1] + ".sha256.stdout";
                    return outpath;
                }
            loadContents: true
            # extract just the hash part
            outputEval: ${
                    return "sha256$" + self[0].contents.trim().split(/ +/)[0];
                }
stdout: ${
        var arr = inputs.filename.path.split("/");
        var outpath = arr[arr.length - 1] + ".sha256.stdout";
        return outpath;
    }
requirements:
- class: InlineJavascriptRequirement