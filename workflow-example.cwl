cwlVersion: v1.0
class: Workflow
id: example-workflow
inputs:
    data_files:
        type:
          - type: array
            items: string
outputs:
    files_out:
        type: File[]
        outputSource: "#generate_files/file_out"
steps:
    generate_files_1:
        run: dd.cwl
        in:
            block_size:
                default: "10M"
            count:
                default: 2
            output_filename:
                default: data_file_1
        out: [file_out]

requirements:
  - class: StepInputExpressionRequirement
  - class: ScatterFeatureRequirement
  - class: MultipleInputFeatureRequirement
  - class: InlineJavascriptRequirement
