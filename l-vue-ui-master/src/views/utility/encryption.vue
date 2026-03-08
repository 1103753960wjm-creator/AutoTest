<script setup lang="ts">
import { Md5 } from "ts-md5";
import { ref } from "vue";
import { Base64 } from "js-base64";
const md5_input = ref<string>("");
const md5_output = ref<any>("");
const md5_encryption = () => {
  const md5 = new Md5();
  md5_output.value = md5.appendStr(md5_input.value.toString()).end();
};

const base64_input = ref<string>("");
const base64_output = ref<string>("");
const base64_encryption = () => {
  base64_output.value = Base64.encode(base64_input.value);
};

const de_base64_input = ref<string>("");
const de_base64_output = ref<string>("");
const de_base64_encryption = () => {
  de_base64_output.value = Base64.decode(de_base64_input.value);
};

const unicode_input = ref<string>("");
const de_unicode_input = ref<string>("");
const unicode_output = ref<string>("");
const de_unicode_output = ref<string>("");
const unicode_encryption = () => {
  unicode_output.value = encodeUnicode(unicode_input.value);
};
const de_unicode_encryption = () => {
  de_unicode_output.value = decodeUnicode(de_unicode_input.value);
};

const encodeUnicode = (str: string) => {
  return str.replace(/[\s\S]/g, function (character: string) {
    return "\\u" + ("0000" + character.charCodeAt(0).toString(16)).slice(-4);
  });
};
const decodeUnicode = (str: string) => {
  return str.replace(/\\u([\d\w]{4})/gi, function (_match: string, grp: string) {
    return String.fromCharCode(parseInt(grp, 16));
  });
};

const url_input = ref<string>("");
const url_output = ref<string>("");
const de_url_input = ref<string>("");
const de_url_output = ref<string>("");
const url_encryption = () => {
  url_output.value = encodeURIComponent(url_input.value);
};
const de_url_encryption = () => {
  de_url_output.value = decodeURIComponent(de_url_input.value);
};
</script>

<template>
  <div style="padding: 10px;">
    <div>
      <koiCard>
        <div>
          <h5>MD5加密：</h5>
          <el-input style="width: 300px; padding-right: 10px;" v-model="md5_input" placeholder="请输入内容" />
          <el-button type="primary" @click="md5_encryption">加密</el-button>
          <el-input style="width: 300px; padding-left: 10px;" v-model="md5_output" placeholder="响应结果" />
        </div>
        <div>
          <h5>Base64加密：</h5>
          <el-input style="width: 300px; padding-right: 10px;" v-model="base64_input" placeholder="请输入内容" />
          <el-button type="primary" @click="base64_encryption">加密</el-button>
          <el-input style="width: 300px; padding-left: 10px;" v-model="base64_output" placeholder="响应结果" />
        </div>
        <div>
          <h5>Base64解密：</h5>
          <el-input style="width: 300px; padding-right: 10px;" v-model="de_base64_input" placeholder="请输入内容" />
          <el-button type="primary" @click="de_base64_encryption">解密</el-button>
          <el-input style="width: 300px; padding-left: 10px;" v-model="de_base64_output" placeholder="响应结果" />
        </div>
        <div>
          <h5>URL加密：</h5>
          <el-input style="width: 300px; padding-right: 10px;" v-model="url_input" placeholder="请输入内容" />
          <el-button type="primary" @click="url_encryption">加密</el-button>
          <el-input style="width: 300px; padding-left: 10px;" v-model="url_output" placeholder="响应结果" />
        </div>
        <div>
          <h5>URL解密：</h5>
          <el-input style="width: 300px; padding-right: 10px;" v-model="de_url_input" placeholder="请输入内容" />
          <el-button type="primary" @click="de_url_encryption">解密</el-button>
          <el-input style="width: 300px; padding-left: 10px;" v-model="de_url_output" placeholder="响应结果" />
        </div>
        <div>
          <h5>Unicode加密：</h5>
          <el-input style="width: 300px; padding-right: 10px;" v-model="unicode_input" placeholder="请输入内容" />
          <el-button type="primary" @click="unicode_encryption">加密</el-button>
          <el-input style="width: 300px; padding-left: 10px;" v-model="unicode_output" placeholder="响应结果" />
        </div>
        <div>
          <h5>Unicode解密：</h5>
          <el-input style="width: 300px; padding-right: 10px;" v-model="de_unicode_input" placeholder="请输入内容" />
          <el-button type="primary" @click="de_unicode_encryption">解密</el-button>
          <el-input style="width: 300px; padding-left: 10px;" v-model="de_unicode_output" placeholder="响应结果" />
        </div>
        <div class="h-10px"></div>
      </koiCard>
    </div>
  </div>
</template>

<style lang="less" scoped></style>
