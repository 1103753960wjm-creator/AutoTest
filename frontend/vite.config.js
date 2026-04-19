import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import Components from 'unplugin-vue-components/vite'
import { ElementPlusResolver } from 'unplugin-vue-components/resolvers'
import { resolve } from 'path'

const manualChunkGroups = {
  'vendor-framework': ['vue', 'vue-router', 'pinia', 'vue-i18n', 'axios', 'dayjs', 'lodash-es'],
  'vendor-excel': ['xlsx'],
  'vendor-dragdrop': ['vuedraggable', 'sortablejs'],
  'vendor-curl-tools': ['curlconverter', 'tree-sitter', 'web-tree-sitter', 'tree-sitter-bash', 'yamljs', 'lossless-json', 'jsesc'],
  'vendor-editor': ['monaco-editor'],
}

const resolveManualChunk = (id) => {
  if (!id.includes('node_modules')) {
    return null
  }

  const normalizedId = id.replace(/\\/g, '/')

  if (normalizedId.includes('/node_modules/element-plus/es/components/')) {
    const componentMatch = normalizedId.match(/\/node_modules\/element-plus\/es\/components\/([^/]+)\//)
    if (componentMatch?.[1]) {
      if (componentMatch[1] === 'table') {
        return 'vendor-ep-table'
      }
    }
  }

  if (normalizedId.includes('/node_modules/element-plus/')) {
    return 'vendor-element-plus-core'
  }

  if (normalizedId.includes('/node_modules/@element-plus/icons-vue/')) {
    return 'vendor-ep-icons'
  }

  if (normalizedId.includes('/node_modules/zrender/')) {
    return 'vendor-zrender'
  }

  if (normalizedId.includes('/node_modules/echarts/')) {
    return 'vendor-echarts'
  }

  for (const [chunkName, packages] of Object.entries(manualChunkGroups)) {
    if (packages.some((pkg) => normalizedId.includes(`/node_modules/${pkg}/`))) {
      return chunkName
    }
  }

  return null
}

export default defineConfig({
  plugins: [
    vue(),
    Components({
      dts: false,
      resolvers: [
        ElementPlusResolver({
          importStyle: 'css'
        })
      ]
    })
  ],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
    },
  },
  css: {
    preprocessorOptions: {
      scss: {
        api: 'modern-compiler', // 使用现代 Sass API
        silenceDeprecations: ['legacy-js-api'], // 静默旧警告
      }
    }
  },
  optimizeDeps: {
    esbuildOptions: {
      target: 'es2022'
    },
    force: true,
    exclude: ['tree-sitter'],
  },
  build: {
    target: 'es2022',
    rollupOptions: {
      output: {
        // 将重依赖拆分到独立 chunk，优先解决主包体积过大的构建告警
        manualChunks(id) {
          return resolveManualChunk(id)
        }
      }
    }
  },
  server: {
    port: 3000,
    host: '0.0.0.0',
    headers: {
      'Cache-Control': 'no-cache, no-store, must-revalidate',
      'Pragma': 'no-cache',
      'Expires': '0',
    },
    proxy: {
      '^/api/': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        secure: false,
      },
      '^/media/': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        secure: false,
      },
      '^/app-automation-templates/': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        secure: false,
      },
      '^/app-automation-reports/': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        secure: false,
      },
      '^/ws/': {
        target: 'ws://127.0.0.1:8000',
        ws: true,
        changeOrigin: true,
        configure: (proxy) => {
          proxy.on('error', () => {})
          proxy.on('proxyReqWs', (proxyReq, req, socket) => {
            socket.on('error', () => {})
          })
        },
      },
    },
  },
  assetsInclude: ['**/*.wasm'],
})
