<script setup lang="ts">
import { computed, ref } from "vue";
import VueJsonPretty from "vue-json-pretty";
import jsonE from "@/components/CodeEditor/jsonE.vue";
import "vue-json-pretty/lib/styles.css";

const props = defineProps({
  req: {
    type: Object,
    default: () => {
      return {};
    }
  },
  res: {
    type: Object,
    default: () => {
      return {};
    }
  },
  env_list: {
    type: Array,
    default: () => {
      return [];
    }
  },
  tree_list: {
    type: Array,
    default: () => {
      return [];
    }
  },
  redis_example_list: {
    type: Array,
    default: () => {
      return ["common"];
    }
  },
  local_db_list: {
    type: Array,
    default: () => {
      return [];
    }
  },
  params_list: {
    type: Array,
    default: () => {
      return [{ name: "", id: null }];
    }
  }
});

const val_type_list = ref([
  { name: "环境变量", value: 1 },
  { name: "全局变量", value: 2 }
]);
const res_type_list = ref([
  { name: "响应结果-JSON", value: 1 },
  { name: "请求头-Headers", value: 2 },
  { name: "请求头-Body", value: 3 },
  { name: "Headers-响应结果", value: 4 },
  { name: "自定义目标值", value: 5 }
]);
const tips = ref<any>(
  '路径示例，结果={"code": 200, "info": {"username": "admin"}, "list": [{"id": 1},{"id": 2}]}\n' +
  "例子：code：$.code, username：$.info.username，数组：$.list[0].id / $.list[1].id分别等于1 / 2"
);
const method_list = ref([
  { name: "GET", value: 1 },
  { name: "POST", value: 2 },
  { name: "PUT", value: 3 },
  { name: "DELETE", value: 4 },
  { name: "PATCH", value: 5 },
  { name: "OPTIONS", value: 6 }
]);
const req_active = ref<any>("body");
const res_active = ref<any>("res");
const env_list = ref<any>([]);
const tree_list = props.tree_list;
const local_db_list = ref<any>([]);
const params_list = ref<any>([{ name: "", id: null }]);
const req = computed(() => ({ ...props.req }));
req.value.body = JSON.stringify(req.value.body) || {};
const res = computed(() => ({ ...props.res }));
</script>

<template>
  <div>
    <koiCard>
      <div>
        <div>
          <div style="border: 1px solid #e4e7ed; width: 98%; padding: 5px; border-radius: 5px">
            <div>
              <el-select v-model="req.method" placeholder="选择请求方法" style="width: 10%">
                <el-option v-for="(method, index) in method_list" :key="index" :label="method.name"
                  :value="method.value">
                </el-option>
              </el-select>
              <el-input v-model="req.url" placeholder="请输入请求地址" clearable
                style="width: 40%; margin-left: 10px; margin-right: 10px">
              </el-input>
            </div>
          </div>
          <div style="border: 1px solid #e4e7ed; border-radius: 5px; width: 98%; padding-left: 10px; height: 320px">
            <el-tabs v-model="req_active" class="demo-tabs">
              <el-tab-pane label="Params" name="params">
                <template #label>
                  <el-badge :show-zero="false" :value="req.params.length" :offset="[13, 2]" type="primary"> Params
                  </el-badge>
                </template>
                <div style="width: 100%; overflow: auto; height: 250px">
                  <div v-for="(params, index) in req.params" :key="index" style="padding-block-end: 5px">
                    <el-checkbox v-model="params.status" />
                    <el-input v-model="params.key" placeholder="请输入参数key" style="width: 40%; padding-left: 10px">
                    </el-input>
                    <el-input v-model="params.value" placeholder="请输入参数value"
                      style="width: 40%; padding-left: 10px; padding-right: 10px">
                    </el-input>
                  </div>
                </div>
              </el-tab-pane>
              <el-tab-pane label="Header" name="header">
                <template #label>
                  <el-badge :show-zero="false" :value="req.header.length" :offset="[13, 2]" type="primary"> Header
                  </el-badge>
                </template>
                <div style="width: 100%; overflow: auto; height: 250px">
                  <div v-for="(header, index) in req.header" :key="index" style="padding-block-end: 5px">
                    <el-checkbox v-model="header.status" />
                    <el-input v-model="header.key" placeholder="请输入参数key" style="width: 40%; padding-left: 10px">
                    </el-input>
                    <el-input v-model="header.value" placeholder="请输入参数value"
                      style="width: 40%; padding-left: 10px; padding-right: 10px">
                    </el-input>
                  </div>
                </div>
              </el-tab-pane>
              <el-tab-pane label="Body" name="body">
                <div style="width: 100%; height: 260px">
                  <div style="width: 10%; float: right; padding-right: 40px; padding-left: 10px">
                    <el-select style="width: 120%; padding-block-end: 30px" v-model="req.params_id" clearable
                      placeholder="非必选：选择参数依赖">
                      <el-option v-for="(params, index) in params_list" :key="index" :label="params.name"
                        :value="params.id">
                      </el-option>
                    </el-select>
                    <el-radio-group v-model="req.body_type">
                      <el-radio :value="1" size="small">None</el-radio>
                      <el-radio :value="2" size="small">JSON</el-radio>
                      <el-radio :value="3" size="small">form-data</el-radio>
                      <el-radio :value="4" size="small">form-urlencoded</el-radio>
                      <el-radio :value="5" size="small">binary</el-radio>
                    </el-radio-group>
                  </div>
                  <div v-if="req.body_type === 2" style="width: 85%; float: left">
                    <jsonE v-model:value="req.body" :height="'260px'" />
                    <!-- <jsonEditor v-model:code="item.content.req.body" :height="'260'" @call_back="body_back" /> -->
                  </div>
                  <div v-if="req.body_type === 3" style="width: 85%; float: left">
                    <div v-for="(form, index) in req.form_data" :key="index" style="padding-block-end: 5px">
                      <el-checkbox v-model="form.status" />
                      <el-input v-model="form.key" placeholder="请输入参数key" style="width: 40%; padding-left: 10px">
                      </el-input>
                      <el-input v-model="form.value" placeholder="请输入参数value"
                        style="width: 40%; padding-left: 10px; padding-right: 10px">
                      </el-input>
                    </div>
                  </div>
                  <div v-if="req.body_type === 4" style="width: 85%; float: left">
                    <div v-for="(form, index) in req.form_urlencoded" :key="index" style="padding-block-end: 5px">
                      <el-checkbox v-model="form.status" />
                      <el-input v-model="form.key" placeholder="请输入参数key" style="width: 40%; padding-left: 10px">
                      </el-input>
                      <el-input v-model="form.value" placeholder="请输入参数value"
                        style="width: 40%; padding-left: 10px; padding-right: 10px">
                      </el-input>
                    </div>
                  </div>
                  <div v-if="req.body_type === 5" style="height: 260px; overflow: auto; width: 84%">
                    <div style="width: 40%; float: left">
                      <div v-for="(file, index) in req.file_path" :key="index">
                        <el-tag type="success">{{ "已上传成功：" + file }}</el-tag>
                      </div>
                    </div>
                  </div>
                </div>
              </el-tab-pane>
              <el-tab-pane name="before">
                <template #label>
                  <el-badge :show-zero="false" :value="req.before.length" :offset="[10, 2]" type="primary"> 前置操作
                  </el-badge>
                </template>
                <div>
                  <div class="h-5px"></div>
                  <div style="padding: 5px; height: 220px; overflow-y: auto">
                    <el-collapse accordion>
                      <el-collapse-item v-for="(pre, index) in req.before" :key="index">
                        <template #title>
                          <span>
                            <span v-if="pre.type === 1">
                              <SvgIcon style="padding-right: 5px" name="API3" width="14" height="14"> </SvgIcon>
                              <span>{{ index + 1 + ". 预请求接口：" + pre.title }}</span>
                            </span>
                            <span v-if="pre.type === 2">
                              <el-icon class="header-icon">
                                <Operation />
                              </el-icon>
                              {{ index + 1 + ". 预设变量：" + pre.name + " 赋值等于 " + pre.value }}
                            </span>
                            <span v-if="pre.type === 3">
                              <el-icon class="header-icon" style="">
                                <Clock />
                              </el-icon>
                              {{ index + 1 + ". 设置等待时长：" + pre.wait_time + "秒" }}
                            </span>
                            <span v-if="pre.type === 4">
                              <el-icon class="header-icon">
                                <EditPen />
                              </el-icon>
                              {{ index + 1 + ". 自定义脚本" + pre.title }}
                            </span>
                          </span>
                        </template>
                        <div v-if="pre.type === 1">
                          <div>
                            <el-form inline>
                              <el-form-item label="操作名称：">
                                <el-input style="width: 300px" v-model="pre.title" placeholder="请输入前置名称"></el-input>
                              </el-form-item>
                              <el-form-item label="选择环境：">
                                <el-select placeholder="请选择环境地址" v-model="pre.env_id" style="width: 300px">
                                  <el-option v-for="(env, index) in env_list" :key="index" :label="env.name"
                                    :value="env.id"></el-option>
                                </el-select>
                              </el-form-item>
                              <el-form-item label="选择接口：">
                                <el-cascader :options="tree_list" v-model="pre.api_id"
                                  :props="{ value: 'api_id', label: 'name', children: 'children' }"
                                  style="width: 705px"></el-cascader>
                              </el-form-item>
                            </el-form>
                          </div>
                        </div>
                        <div v-if="pre.type === 2">
                          <el-form inline>
                            <el-form-item label="变量名：">
                              <el-input style="width: 200px" v-model="pre.name" placeholder="请输入变量名"></el-input>
                            </el-form-item>
                            <el-form-item label="变量类型：">
                              <el-select placeholder="请选择变量类型" v-model="pre.env_type" style="width: 200px">
                                <el-option v-for="(type, index) in val_type_list" :key="index" :label="type.name"
                                  :value="type.value"></el-option>
                              </el-select>
                            </el-form-item>
                            <el-form-item label="预期值：">
                              <el-input style="width: 200px" v-model="pre.value" placeholder="请输入预期值"></el-input>
                            </el-form-item>
                          </el-form>
                        </div>
                        <div v-if="pre.type === 3">
                          <div>
                            <el-form inline>
                              <el-form-item label="等待时间(秒)：">
                                <el-input-number style="width: 200px" :min="0" :max="60" v-model="pre.wait_time"
                                  placeholder="请输入等待时间"></el-input-number>
                              </el-form-item>
                            </el-form>
                          </div>
                        </div>
                        <div v-if="pre.type === 4">
                          <div>
                            <div>
                              <pythoneditor v-model:value="pre.code" />
                            </div>
                            <div style="float: right"></div>
                          </div>
                        </div>
                      </el-collapse-item>
                    </el-collapse>
                  </div>
                </div>
              </el-tab-pane>
              <el-tab-pane name="after">
                <template #label>
                  <el-badge :show-zero="false" :value="req.after.length" :offset="[10, 2]" type="primary"> 后置操作
                  </el-badge>
                </template>
                <div>
                  <div class="h-5px"></div>
                  <div style="padding: 5px; height: 220px; overflow-y: auto">
                    <el-collapse accordion>
                      <el-collapse-item v-for="(after, index) in req.after" :key="index">
                        <template #title>
                          <span>
                            <span v-if="after.type === 1">
                              <el-icon class="header-icon">
                                <Operation />
                              </el-icon>
                              {{ index + 1 + ". 提取变量：提取 ' " + after.name + " ' 赋值给 ' " + after.value + " '" }}
                            </span>
                            <span v-if="after.type === 2">
                              <el-icon class="header-icon" style="">
                                <Clock />
                              </el-icon>
                              {{ index + 1 + ". 设置等待时长：" + after.wait_time + "秒" }}
                            </span>
                          </span>
                        </template>
                        <div v-if="after.type === 1">
                          <el-form inline>
                            <el-form-item>
                              <template #label>
                                <el-tooltip :content="tips" raw-content>
                                  <el-button type="text" style="color: #000" icon="InfoFilled"></el-button>
                                </el-tooltip>
                                路径:
                              </template>
                              <el-input style="width: 300px" v-model="after.name" placeholder="请输入路径"></el-input>
                            </el-form-item>
                            <el-form-item label="提取目标:">
                              <el-select placeholder="请选择提取目标" v-model="after.res_type" style="width: 300px">
                                <el-option v-for="(res, index) in res_type_list" :key="index" :label="res.name"
                                  :value="res.value"></el-option>
                              </el-select>
                            </el-form-item>
                            <el-form-item label="变量类型:">
                              <el-select placeholder="请选择变量类型" v-model="after.env_type" style="width: 300px">
                                <el-option v-for="(type, index) in val_type_list" :key="index" :label="type.name"
                                  :value="type.value"></el-option>
                              </el-select>
                            </el-form-item>
                            <el-form-item label="变量名:">
                              <el-input style="width: 300px" v-model="after.value" placeholder="请输入变量名"></el-input>
                            </el-form-item>
                          </el-form>
                        </div>
                        <div v-if="after.type === 2">
                          <div>
                            <el-form inline>
                              <el-form-item label="等待时间(秒)：">
                                <el-input-number style="width: 200px" :min="0" :max="60" v-model="after.wait_time"
                                  placeholder="请输入等待时间"></el-input-number>
                              </el-form-item>
                            </el-form>
                          </div>
                        </div>
                      </el-collapse-item>
                    </el-collapse>
                  </div>
                </div>
              </el-tab-pane>
              <el-tab-pane name="assert">
                <template #label>
                  <el-badge :show-zero="false" :value="req.assert.length" :offset="[10, 2]" type="primary"> 断言
                  </el-badge>
                </template>
                <div>
                  <div class="h-5px"></div>
                  <div style="padding: 5px; height: 220px; overflow-y: auto">
                    <el-collapse accordion>
                      <el-collapse-item v-for="(assert, index) in req.assert" :key="index">
                        <template #title>
                          <span>
                            <span v-if="assert.type === 1">
                              <el-icon class="header-icon">
                                <CircleCheck />
                              </el-icon>
                              {{ index + 1 + ". 响应断言：断言 ' " + assert.name + " ' 等于 ' " + assert.value + " '" }}
                            </span>
                            <span v-if="assert.type === 4">
                              <el-icon class="header-icon">
                                <Coin />
                              </el-icon>
                              {{
                                index +
                                1 +
                                ". 直连-数据库断言：查询表 ' " +
                                assert.local_db_table +
                                " ' 条件： " +
                                "' " +
                                assert.local_db_where +
                                " '"
                              }}
                            </span>
                          </span>
                        </template>
                        <div v-if="assert.type === 1">
                          <el-form inline>
                            <el-form-item>
                              <template #label>
                                <el-tooltip :content="tips" raw-content>
                                  <el-button type="text" style="color: #000" icon="InfoFilled"></el-button>
                                </el-tooltip>
                                路径:
                              </template>
                              <el-input style="width: 220px" v-model="assert.name" placeholder="请输入路径"></el-input>
                            </el-form-item>
                            <el-form-item label="断言对象:">
                              <el-select placeholder="请选择断言对象" v-model="assert.res_type" style="width: 220px">
                                <el-option v-for="(res, index) in res_type_list" :key="index" :label="res.name"
                                  :value="res.value"></el-option>
                              </el-select>
                            </el-form-item>
                            <el-form-item label="预期值:">
                              <el-input style="width: 220px" v-model="assert.value" placeholder="请输入预期值"></el-input>
                            </el-form-item>
                          </el-form>
                        </div>
                        <div v-if="assert.type == 4">
                          <div style="width: 100%">
                            <div style="width: 40%; float: left; padding-right: 50px">
                              <el-form>
                                <el-form-item label="选择数据库:">
                                  <el-select v-model="assert.local_db">
                                    <el-option v-for="(db, index) in local_db_list" :key="index" :label="db.name"
                                      :value="db.id"></el-option>
                                  </el-select>
                                </el-form-item>
                                <el-form-item label="数据库表:">
                                  <el-input v-model="assert.local_db_table" placeholder="请输入数据库表名"></el-input>
                                </el-form-item>
                                <el-form-item label="条件(where):">
                                  <el-input v-model="assert.local_db_where"
                                    placeholder="请输入筛选条件，与where条件一致，例：game_id=50001 and xxx=xxx"></el-input>
                                </el-form-item>
                              </el-form>
                            </div>
                            <div style="
                                width: 50%;
                                float: left;
                                border: 1px solid #e4e7ed;
                                padding: 5px;
                                height: 150px;
                                overflow-y: auto;
                                border-radius: 5px;
                              ">
                              <div v-for="(form, index) in assert.local_db_assert" :key="index"
                                style="padding-block-end: 5px">
                                <el-input v-model="form.name" placeholder="请输入表字段名"
                                  style="width: 30%; padding-left: 10px">
                                </el-input>
                                <el-select placeholder="请断言目标" v-model="form.type"
                                  style="width: 25%; padding-left: 10px">
                                  <el-option v-for="(res, index) in res_type_list" :key="index" :label="res.name"
                                    :value="res.value"></el-option>
                                </el-select>
                                <el-input v-model="form.value" placeholder="请输入预期值"
                                  style="width: 30%; padding-left: 10px; padding-right: 10px">
                                </el-input>
                              </div>
                            </div>
                          </div>
                        </div>
                      </el-collapse-item>
                    </el-collapse>
                  </div>
                </div>
              </el-tab-pane>
              <el-tab-pane label="配置" name="config">
                <div>
                  <el-form v-model="req.config" label-position="right">
                    <el-form-item label="重试次数(次)：">
                      <el-input-number v-model="req.config.retry"></el-input-number>
                    </el-form-item>
                    <el-form-item label="接口连接超时(秒)：">
                      <el-input-number v-model="req.config.req_timeout"></el-input-number>
                    </el-form-item>
                    <el-form-item label="结果读取超时(秒)：">
                      <el-input-number v-model="req.config.res_timeout"></el-input-number>
                    </el-form-item>
                  </el-form>
                </div>
              </el-tab-pane>
            </el-tabs>
          </div>
          <div style="border: 1px solid #e4e7ed; border-radius: 5px; width: 98%; padding-left: 10px; height: 320px">
            <el-tabs v-model="res_active" class="demo-tabs">
              <el-tab-pane label="响应-结果" name="res">
                <div>
                  <vue-json-pretty v-model:data="res.body" :height="260" :showIcon="true" :showLine="true"
                    :virtual="true" :showSelectController="true" />
                </div>
              </el-tab-pane>
              <el-tab-pane label="响应-Header" name="res_log">
                <div>
                  <vue-json-pretty v-model:data="res.header" :height="260" :showIcon="true" :showLine="true"
                    :virtual="true" :showSelectController="true" />
                </div>
              </el-tab-pane>
              <el-tab-pane name="before_res">
                <template #label>
                  <el-badge :show-zero="false" :value="res.before.length" :offset="[10, 2]"
                    type="danger">前置操作结果</el-badge>
                </template>
                <div style="padding-left: 10px; height: 260px; overflow-y: auto">
                  <el-collapse>
                    <el-collapse-item v-for="(before, index) in res.before">
                      <template #title>
                        <span v-if="before.status === 0" style="color: rgb(219, 97, 120)">{{
                          index + 1 + ". " + before.message
                        }}</span>
                        <span v-if="before.status === 1" style="color: rgb(46, 134, 234)">{{
                          index + 1 + ". " + before.message
                        }}</span>
                      </template>
                      <div v-if="before.type === 1">
                        <vue-json-pretty v-model:data="before.content.body" :height="160" :showIcon="true"
                          :showLine="true" :virtual="true" :showSelectController="true" />
                      </div>
                    </el-collapse-item>
                  </el-collapse>
                </div>
              </el-tab-pane>
              <el-tab-pane name="after_res">
                <template #label>
                  <el-badge :show-zero="false" :value="res.after.length" :offset="[10, 2]"
                    type="danger">后置操作结果</el-badge>
                </template>
                <div style="padding-left: 10px; height: 260px; overflow-y: auto">
                  <el-collapse>
                    <el-collapse-item v-for="(after, index) in res.after">
                      <template #title>
                        <span v-if="after.status === 0" style="color: rgb(219, 97, 120)">{{
                          index + 1 + ". " + after.message
                        }}</span>
                        <span v-if="after.status === 1" style="color: rgb(46, 134, 234)">{{
                          index + 1 + ". " + after.message
                        }}</span>
                      </template>
                    </el-collapse-item>
                  </el-collapse>
                </div>
              </el-tab-pane>
              <el-tab-pane label="断言结果" name="assert_res">
                <template #label>
                  <el-badge :show-zero="false" :value="res.assert.length" :offset="[10, 2]"
                    type="danger">断言结果</el-badge>
                </template>
                <div style="padding-left: 10px; height: 260px; overflow-y: auto">
                  <el-collapse>
                    <el-collapse-item v-for="(assert, index) in res.assert">
                      <template #title>
                        <span v-if="assert.status === 0" style="color: rgb(219, 97, 120)">{{
                          index + 1 + ". " + assert.message
                        }}</span>
                        <span v-if="assert.status === 1" style="color: rgb(46, 134, 234)">{{
                          index + 1 + ". " + assert.message
                        }}</span>
                      </template>
                    </el-collapse-item>
                  </el-collapse>
                </div>
              </el-tab-pane>
              <el-tab-pane disabled style="float: right">
                <template #label>
                  <div class="tab-info">
                    <i class="el-icon-monitor" style="font-size: 16px" />
                    <span slot="code" class="code">状态码：{{ res.code }}</span>
                  </div>
                </template>
              </el-tab-pane>
              <el-tab-pane disabled>
                <template #label>
                  <div class="tab-info">
                    <i class="el-icon-document" style="font-size: 16px" />
                    <span slot="size" class="size">资源大小：{{ res.size }} B</span>
                  </div>
                </template>
              </el-tab-pane>
              <el-tab-pane disabled>
                <template #label>
                  <div class="tab-info">
                    <i class="el-icon-time" style="font-size: 16px" />
                    <span slot="size" class="size">响应时间：{{ res.res_time }} ms</span>
                  </div>
                </template>
              </el-tab-pane>
            </el-tabs>
          </div>
        </div>
      </div>
    </koiCard>
  </div>
</template>

<style lang="scss" scoped>
.el-collapse-item__content {
  padding-bottom: 5px !important;
}

.el-collapse-item__header {
  height: 35px !important;
}

.code,
.size {
  font-size: 14px;
  color: rgb(45, 23, 241);
  margin-left: 5px;
}
</style>
