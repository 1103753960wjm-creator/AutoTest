<template>
  <div class="page-container">
    <!-- 顶部卡片区域 -->
    <el-card class="top-card">
      <div class="card-content">
        <!-- 左侧表单项 -->
        <el-form :inline="true">
          <el-form-item>
            <el-input v-model="searchForm.keyword" placeholder="请输入关键字"></el-input>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleSearch">搜索</el-button>
          </el-form-item>
        </el-form>
      </div>
    </el-card>

    <!-- 中间主要内容区域 -->
    <div class="main-content">
      <!-- 左侧列表 -->
      <el-card class="left-panel">
        <div class="list-container">
          <el-tree
            :data="treeData"
            @node-click="handleNodeClick"
            :props="defaultProps">
          </el-tree>
        </div>
      </el-card>

      <!-- 右侧详情 -->
      <el-card class="right-panel">
        <div class="detail-container">
          <!-- 根据手稿显示的详情内容 -->
          <el-descriptions :column="1" border>
            <el-descriptions-item label="名称">示例名称</el-descriptions-item>
            <el-descriptions-item label="状态">正常</el-descriptions-item>
            <!-- 其他详情项 -->
          </el-descriptions>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script>
export default {
  name: 'SomePage',
  data() {
    return {
      searchForm: {
        keyword: ''
      },
      treeData: [], // 树形数据
      defaultProps: {
        children: 'children',
        label: 'label'
      }
    }
  },
  methods: {
    handleSearch() {
      // 搜索处理
    },
    handleNodeClick(data) {
      // 树节点点击处理
    }
  }
}
</script>

<style scoped>
.page-container {
  padding: 20px;
}

.top-card {
  margin-bottom: 20px;
}

.main-content {
  display: flex;
  gap: 20px;
}

.left-panel {
  width: 300px;
}

.right-panel {
  flex: 1;
}

.list-container {
  min-height: 400px;
}

.detail-container {
  padding: 20px;
}
</style>
