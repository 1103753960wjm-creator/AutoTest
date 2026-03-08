<template>
  <div style="padding: 10px">
    <div style="float: right">
      <div>
        <el-button class="floating-button" @click="formatJson">漂亮</el-button>
      </div>
      <div style="margin-top: 10px">
        <el-button class="floating-button" @click="formatJson2">压缩</el-button>
      </div>
      <div style="margin-top: 10px">
        <el-button class="floating-button" @click="clear">清空</el-button>
      </div>
    </div>
    <Codemirror v-model:value="code" :options="cmOptions" :height="800" width="96%" class="cm-component" :border="true"
      @ready="onReady">
    </Codemirror>
  </div>
</template>
<script lang="ts" setup>
import { ref, reactive } from "vue";
import { Editor, EditorConfiguration } from "codemirror";
import Codemirror from "codemirror-editor-vue3";
// @ts-ignore
import jsonlint from "jsonlint-mod-fixed";
// language json or js
import "codemirror/mode/javascript/javascript.js";
import "codemirror/addon/lint/lint.css";
import "codemirror/addon/lint/lint.js";
import "codemirror/addon/lint/json-lint";
// @ts-ignore
window.jsonlint = jsonlint;

const code = ref(
  `{}`
);

const cmOptions: EditorConfiguration = reactive({
  mode: "application/json",
  lineNumbers: true,
  lineWiseCopyCut: true,
  gutters: ["CodeMirror-lint-markers"],
  lint: true
});

const cminstance = ref<Editor | null>(null);
const onReady = (cm: Editor) => {
  cminstance.value = cm;
  console.log(cm.getValue());
};

defineExpose({
  setTheme: (theme: string) => {
    console.log(" theme", theme);
    cminstance.value?.setOption("theme", theme);
  }
});

const formatJson = () => {
  code.value = JSON.stringify(JSON.parse(code.value), null, 4);
};

const formatJson2 = () => {
  code.value = JSON.stringify(JSON.parse(code.value), null, 0);
};

const clear = () => {
  code.value = JSON.stringify({}, null, 4);
};
</script>
<style lang="scss" scoped>
.cm-component {
  font-family: monospace;
}

.floating-button {
  bottom: 20px;
  /* 距离底部 */
  right: 20px;
  /* 距离右侧 */
  background-color: #007bff;
  /* 按钮颜色 */
  color: white;
  /* 文字颜色 */
  border: none;
  /* 去除边框 */
  box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.2);
  /* 阴影效果 */
  font-size: 16px;
  /* 字体大小 */
  cursor: pointer;
  /* 鼠标样式 */
  transition:
    transform 0.2s ease,
    box-shadow 0.2s ease;
  /* 动画过渡效果 */
}

.floating-button:hover {
  transform: scale(1.1);
  /* 放大效果 */
  box-shadow: 0px 6px 10px rgba(0, 0, 0, 0.3);
  /* 增强阴影 */
}
</style>
