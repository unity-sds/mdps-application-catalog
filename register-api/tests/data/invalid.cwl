#!/usr/bin/env cwl-runner
cwlVersion: v1.2
$namespaces:
      cwltool: http://commonwl.org/cwltool#
$graph:
  - class: Workflow
    id: main
    label: Workflow that executes the SBG/Sister isofit workflow
    
    requirements:
      InlineJavascriptRequirement: {}
      NetworkAccess:
        networkAccess: true
      StepInputExpressionRequirement: {}
      SubworkflowFeatureRequirement: {}

    inputs:
      parameters:
        type:
          fields:
            crid:
            - 'null'
            - string
            output_collection:
            - 'null'
            - string
            sensor:
            - 'null'
            - string
            temp_directory:
            - 'null'
            - string
            cores:
            - 'null'
            - int
          type: record
      stage_in:
        type:
          fields:
            download_type: string
            downloading_keys:
            - string
            - 'null'
            edl_password:
            - string
            - 'null'
            edl_password_type:
            - string
            - 'null'
            edl_username:
            - string
            - 'null'
            stac_json: 
            - string
            - File
          type: record
      stage_out:
        type:
          fields:
            aws_access_key_id:
            - string
            - 'null'
            aws_region:
            - string
            - 'null'
            aws_secret_access_key:
            - string
            - 'null'
            aws_session_token:
            - string
            - 'null'
            collection_id:
            - string
            - 'null'
            staging_bucket:
            - string
            - 'null'
          type: record
      stage_aux_in:
        type:
          fields:
            download_type: string
            downloading_keys:
            - string
            - 'null'
            edl_password:
            - string
            - 'null'
            edl_password_type:
            - string
            - 'null'
            edl_username:
            - string
            - 'null'
            stac_json: 
            - string
            - File
          type: record
    outputs:
      stage_out_results:
        outputSource: stage_out/stage_out_results
        type: File
      stage_out_success:
        outputSource: stage_out/successful_features
        type: File
      stage_out_failures:
        outputSource: stage_out/failed_features
        type: File

    steps:
      process:
          run: "#unity-isofit"
          in:
            #catalog_name: input_catalog_name
            crid:
              source: parameters
              valueFrom: $(self.crid)
            download_dir: stage_in/stage_in_download_dir
            aux_dir: stage_aux_in/stage_in_download_dir
            output_collection: 
              source: parameters
              valueFrom: $(self.output_collection)
            cores: 
              source: parameters
              valueFrom: $(self.cores)
          out: [process_output_dir]
      stage_in:
        in:
          download_type:
            source: stage_in
            valueFrom: $(self.download_type)
          downloading_keys:
            source: stage_in
            valueFrom: $(self.downloading_keys)
          edl_password:
            source: stage_in
            valueFrom: $(self.edl_password)
          edl_password_type:
            source: stage_in
            valueFrom: $(self.edl_password_type)
          edl_username:
            source: stage_in
            valueFrom: $(self.edl_username)
          stac_json:
            source: stage_in
            valueFrom: $(self.stac_json)
        out:
        - stage_in_collection_file
        - stage_in_download_dir
        run: stage_in.cwl
      stage_aux_in:
        in:
          download_type:
            source: stage_in
            valueFrom: $(self.download_type)
          downloading_keys:
            source: stage_in
            valueFrom: $(self.downloading_keys)
          edl_password:
            source: stage_in
            valueFrom: $(self.edl_password)
          edl_password_type:
            source: stage_in
            valueFrom: $(self.edl_password_type)
          edl_username:
            source: stage_in
            valueFrom: $(self.edl_username)
          stac_json:
            source: stage_aux_in
            valueFrom: $(self.stac_json)
        out:
        - stage_in_collection_file
        - stage_in_download_dir
        run: stage_in.cwl
      stage_out:
        in:
          aws_access_key_id:
            source: stage_out
            valueFrom: $(self.aws_access_key_id)
          aws_secret_access_key:
            source: stage_out
            valueFrom: $(self.aws_secret_access_key)
          aws_session_token:
            source: stage_out
            valueFrom: $(self.aws_session_token)
          collection_id:
            source: stage_out
            valueFrom: $(self.collection_id)
          output_dir: process/process_output_dir
          staging_bucket:
            source: stage_out
            valueFrom: $(self.staging_bucket)
        out:
        - stage_out_results
        - successful_features
        - failed_features
        run: stage_out.cwl
    
  - class: CommandLineTool
    id: "unity-isofit"
    label: "emit isofit"
    cwlVersion: v1.2
    
    requirements:
      - class: DockerRequirement
        dockerPull: "429178552491.dkr.ecr.us-west-2.amazonaws.com/unity/sbg-unity-isofit:56ca9250"
    
    
    arguments:
    - $(inputs.download_dir.path)/$(inputs.catalog_name)
    - $(runtime.outdir)
    - $(inputs.aux_dir.path)/$(inputs.emulator_name)
    - $(inputs.crid)
    - $(inputs.output_collection)
    - $(inputs.cores)
    inputs:
      catalog_name:
        type: string
        default: stage-in-results.json
      emulator_name:
        type: string
        default: sRTMnet_v120.h5
      crid:
        default: '001'
        type: string
      download_dir:
        type:  Directory
      output_collection:
        default: L1B_processed
        type: string
      cores:
        default: 4 
        type: int
      aux_dir:
        type: Directory
      sensor:
        default: EMIT
        type: string
      temp_directory:
        default: /unity/ads/temp/nb_l1b_preprocess
        type: string
    
    outputs:
      process_output_dir:
        outputBinding:
          glob: $(runtime.outdir)
        type: Directory
    
    baseCommand: ["python", "/app/process.py"]