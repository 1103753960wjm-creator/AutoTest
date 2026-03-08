<script setup lang="ts">
const addTask = () => {
}
</script>

<template>
    <div class="pressure">
        <div class="pressure-title">
            <div class="pressure-title-left">
                <div class="pressure-title-left-title">
                    <iframe style="width: 800px; height: 800px;" src="https://ops.sl916.com/grafana" />
                </div>
                <div class="pressure-title-left-content">
                    <el-button type="primary" @click="addTask">添加压测任务</el-button>
                </div>
            </div>
        </div>
    </div>
</template>

<style scss scoped></style>