# ComfyUI-HP-SaveImageBatchAsJSON

由于循环需要，单独生成base64文件将给后续循环带来list数量级别的输入导致报错或者拖延，故选择将batch转换成base64编码的json文件并保存。
需配合json解码程序使用，将json解码成单帧图片。

batch_index和total_batch_size是用于编写json内部图片名称的接口，内部图片名称编写规则为：batch_index * total_batch_size作为开端续写图片名称。
batch_index接口可连接循环index编号，total_batch_size可填写批次大小，如果都不填默认为0，每批次解码后名称都是0开头。

Implementation Note: Base64 JSON Batch Saver

Objective: To prevent potential errors and significant slowdowns caused by passing list-level inputs (individual Base64 files) in ComfyUI's loop structure (Map function), the node converts the entire image batch into a single Base64-encoded JSON dictionary file.

Usage: This JSON file must be processed using a dedicated external decoder program to be converted back into individual image frames.

Global Naming Logic:
The inputs 'batch_index' and 'total_batch_size' are used to calculate the globally unique starting index for images within the JSON.

The internal image naming rule is based on:
Global Frame Index = batch_index * total_batch_size + frame_in_batch_index

* The 'batch_index' input should be connected to the loop's index counter.
* The 'total_batch_size' is the batch size specified in the workflow.
* Default Behavior: If both inputs are left unconnected or set to zero, the indexing will start at 0 for every batch's decoded frames.
