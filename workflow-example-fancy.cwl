cwlVersion: v1.0
class: Workflow
id: example-workflow
inputs:
    data_files:
        type:
          - type: array
            items: string
    block_size:
        type:
          - "null" # makes it optional
          - type: array
            items: ["null", string]
          - type: 
            #default: $(Array(inputs.data_files.size()).fill("10M"))
outputs:
    files_out:
        type: File[]
        outputSource: "#generate_files/file_out"
steps:
    generate_files:
        run: dd.cwl
        scatter: output_filename
        scatterMethod: dotproduct
        in:
            block_size:
                default: "10M"
            count:
                default: 2
            output_filename:
                source: "#data_files"
        out: [file_out]



requirements:
  - class: StepInputExpressionRequirement
  - class: ScatterFeatureRequirement
  - class: MultipleInputFeatureRequirement
  - class: InlineJavascriptRequirement
