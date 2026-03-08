<template>
  <Codemirror
    v-model:value="code"
    :options="cmOptions"
    border
    ref="cmRef"
    height="150"
    width="80%"
    @change="onChange"
    @input="onInput"
    @ready="onReady"
  />
</template>

<script>
import { ref } from "vue";
import Codemirror from "codemirror-editor-vue3";
import "codemirror/mode/python/python.js";

export default {
  components: { Codemirror },
  setup() {
    const code = ref("");
    const cmOptions = {
      mode: "text/x-python",
      theme: "default",
      lineNumbers: true,
      lineWrapping: true,
      lint: true,
      styleActiveLine: true,
      readonly: true,
      viewportMargin: Infinity, // 使编辑器自动匹配容器大小
      gutters: ['CodeMirror-lint-markers'],
      placeholder: ""
    };

    const onChange = newCode => {
      console.log("Code changed:", newCode);
    };

    const onInput = newCode => {
      console.log("Input event:", newCode);
    };

    const onReady = () => {
      console.log("Codemirror is ready!");
    };

    return {
      code,
      cmOptions,
      onChange,
      onInput,
      onReady
    };
  }
};
</script>
