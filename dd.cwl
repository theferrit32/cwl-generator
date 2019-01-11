cwlVersion: v1.0
class: CommandLineTool
baseCommand: dd
inputs:
    block_size:
        type: string
        inputBinding:
            position: 1
            prefix: bs=
            separate: False
    count:
        type: int
        inputBinding:
            position: 2
            prefix: count=
            separate: False
    output_filename:
        type: string
        inputBinding:
            position: 4
            prefix: of=
            separate: False
    input_file:
        type: string?
        default: /dev/urandom
        inputBinding:
            position: 3
            prefix: if=
            separate: False
outputs:
    file_out:
        type: File
        outputBinding:
            glob: $(inputs.output_filename)