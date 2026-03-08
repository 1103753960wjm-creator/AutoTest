<template>
  <div style=" width: 97%;">
    <div style="float: right; width: 8%">
      <div>
        <el-button plain type="primary" @click="formatJson">格式化</el-button>
      </div>
      <div style="margin-top: 10px">
        <el-button plain type="primary" @click="formatJson2">压缩</el-button>
      </div>
      <div style="margin-top: 10px">
        <el-button plain type="primary" @click="clear">清空</el-button>
      </div>
    </div>
    <div style="width: 90%;">
      <Codemirror style="border: 1px solid #e4e7ed" v-model:value="show_code" :options="cmOptions" :height="props.height" width="100%" class="cm-component"
        :border="true" @ready="onReady" @change="onChange">
      </Codemirror>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { ref, reactive, onMounted, watch } from "vue";
import { Editor, EditorConfiguration } from "codemirror";
import Codemirror from "codemirror-editor-vue3";
// import { jsonlint } from "jsonlint-mod-fixed";
// language json or js
import "codemirror/mode/javascript/javascript.js";
import "codemirror/addon/lint/lint.css";
import "codemirror/addon/lint/lint.js";
import "codemirror/addon/lint/json-lint";

const props = defineProps({
  code: {
    type: String,
    default: `{}`
  },
  height: {
    type: String,
    default: "800px"
  },
  width: {
    type: String,
    default: "100%"
  }
});

const emit = defineEmits(["call_back"]);

watch(() => props.code, (newVal) => {
  show_code.value = newVal;
});

const code_value = ref<any>(props.code);

const show_code = ref<any>({});

// window.jsonlint = jsonlint;

const cmOptions: EditorConfiguration = reactive({
  mode: "javascript",
  theme: "default",
  lineNumbers: true,
  lineWiseCopyCut: true,
  readOnly: false,
  gutters: ["CodeMirror-lint-markers"],
  lint: true,
  styleActiveLine: true, // 激活当前行
  autoCloseBrackets: true,
  line: true,
  viewportMargin: Infinity,
  extraKeys: {
      // 触发提示按键
      ['Ctrl']: 'autocomplete'
    },
  hintOptions: {
      // 自定义提示选项
      completeSingle: false, // 当匹配只有一项的时候是否自动补全
      tables: {} // 代码提示
    },
  
});

const onChange = (value: any, cm: Editor) => {
  console.log(cm)
  emit("call_back", JSON.parse(value));
};

const cminstance = ref<Editor | null>(null);
const onReady = (cm: Editor) => {
  cminstance.value = cm;
};

defineExpose({
  setTheme: (theme: string) => {
    cminstance.value?.setOption("theme", theme);
  },
});

const formatJson = () => {
  show_code.value = JSON.stringify(JSON.parse(show_code.value), null, 4);
  emit("call_back", show_code.value);
};

const formatJson2 = () => {
  show_code.value = JSON.stringify(JSON.parse(show_code.value), null, 0);
  emit("call_back", show_code.value);
};

const clear = () => {
  show_code.value = JSON.stringify({}, null, 4);
  emit("call_back", show_code.value);
};

onMounted(() => {
  show_code.value = code_value.value;
  emit("call_back", show_code.value);
});
</script>

<style lang="scss" scoped>
.cm-component {
  font-family: monospace;
}
// .floating-button {
//   bottom: 20px; /* 距离底部 */
//   right: 20px; /* 距离右侧 */
//   background-color: #007bff; /* 按钮颜色 */
//   color: white; /* 文字颜色 */
//   border: none; /* 去除边框 */
//   box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.2); /* 阴影效果 */
//   font-size: 16px; /* 字体大小 */
//   cursor: pointer; /* 鼠标样式 */
//   transition: transform 0.2s ease, box-shadow 0.2s ease; /* 动画过渡效果 */
// }

// .floating-button:hover {
//   transform: scale(1.1); /* 放大效果 */
//   box-shadow: 0px 6px 10px rgba(0, 0, 0, 0.3); /* 增强阴影 */
// }
</style>
