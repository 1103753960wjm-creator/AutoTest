<script setup lang="ts">
import { development_history } from '@/api/api_question/question';
import { onMounted, ref } from 'vue';


const history = ref<any>([]);


const get_history = async () => {
    const res: any = await development_history({
    });
    history.value = res.data;
}

onMounted(() => {
    get_history();
})
</script>

<template>
    <div style="padding: 10px;">
        <koiCard style="height: 780px; overflow: auto">
            <el-timeline>
                <el-timeline-item v-for="(activity, index) in history" :key="index" type="success"
                    :timestamp="activity.username + '：' + activity.create_time">
                    <span>
                        <span>{{ activity.note }}</span>
                    </span>
                </el-timeline-item>
            </el-timeline>
        </koiCard>
    </div>
</template>

<style scoped lang="scss"></style>