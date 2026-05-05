<template>
  <div class="app-shell">
    <router-view />

    <div v-show="launcherVisible" class="assistant-launcher-wrap">
      <el-button
        class="assistant-launcher"
        type="primary"
        circle
        size="large"
        @click="openAssistantDrawer"
      >
        <el-icon :size="22">
          <ChatDotRound />
        </el-icon>
      </el-button>
      <div class="assistant-launcher-label">AI 小助手</div>
    </div>

    <el-drawer
      v-model="drawerVisible"
      class="assistant-drawer"
      direction="rtl"
      size="380px"
      :modal="true"
      :close-on-click-modal="true"
      :show-close="false"
      :with-header="false"
      @open="launcherVisible = false"
      @closed="launcherVisible = true"
    >
      <div class="assistant-panel">
        <div class="assistant-header">
          <div>
            <div class="assistant-title">智能导购助手</div>
            <div class="assistant-subtitle">这里是 agent 对话模板，后续可接入真实服务</div>
          </div>
          <el-button text @click="closeAssistantDrawer">收起</el-button>
        </div>

        <el-alert
          class="assistant-tip"
          title="点击页面空白区域即可收回抽屉"
          type="info"
          :closable="false"
          show-icon
        />

        <div class="assistant-shortcuts">
          <el-tag
            v-for="item in quickPrompts"
            :key="item"
            effect="light"
            round
            class="assistant-tag"
            @click="applyPrompt(item)"
          >
            {{ item }}
          </el-tag>
        </div>

        <el-scrollbar ref="scrollbarRef" class="assistant-messages">
          <div class="message-list">
            <div
              v-for="message in messages"
              :key="message.id"
              class="message-row"
              :class="`is-${message.role}`"
            >
              <div class="message-bubble">
                <div class="message-role">{{ message.role === 'assistant' ? '小助手' : '我' }}</div>
                <div class="message-content">{{ message.content }}</div>
              </div>
            </div>
          </div>
        </el-scrollbar>

        <div class="assistant-composer">
          <el-input
            v-model="draftMessage"
            type="textarea"
            :rows="4"
            resize="none"
            placeholder="输入你的问题，例如：帮我找畅销书 / 查询订单 / 推荐商品"
            @keydown.enter.exact.prevent="sendMessage"
          />
          <div class="composer-actions">
            <span class="composer-hint">Enter 发送，Shift + Enter 换行</span>
            <el-button type="primary" @click="sendMessage">发送</el-button>
          </div>
        </div>
      </div>
    </el-drawer>
  </div>
</template>

<script setup>
import { nextTick, ref } from 'vue'

const drawerVisible = ref(false)
const launcherVisible = ref(true)
const draftMessage = ref('')
const scrollbarRef = ref(null)
const quickPrompts = ['推荐今天热销', '帮我查订单', '解释支付流程', '联系人工客服']

const messages = ref([
  {
    id: 1,
    role: 'assistant',
    content: '你好，我是你的书店小助手。你可以直接提问，我会帮你梳理商品、订单和支付相关信息。'
  },
])

let messageId = 1

const scrollToBottom = async () => {
  await nextTick()
  const scrollbar = scrollbarRef.value
  const wrap = scrollbar?.wrapRef

  if (wrap) {
    wrap.scrollTop = wrap.scrollHeight
  }
}

const pushMessage = async (role, content) => {
  messageId += 1
  messages.value.push({
    id: messageId,
    role,
    content,
  })
  await scrollToBottom()
}

const applyPrompt = (prompt) => {
  draftMessage.value = prompt
}

const openAssistantDrawer = () => {
  launcherVisible.value = false
  drawerVisible.value = true
}

const closeAssistantDrawer = () => {
  drawerVisible.value = false
}

const sendMessage = async () => {
  const content = draftMessage.value.trim()

  if (!content) {
    return
  }

  draftMessage.value = ''
  await pushMessage('user', content)

  await pushMessage('assistant', '这是对话模板占位区，后续可以在这里接入你的 Agent 接口、流式输出和工具调用。')
}
</script>

<style scoped>
.app-shell {
  min-height: 100vh;
}

.assistant-launcher-wrap {
  position: fixed;
  right: 24px;
  bottom: 24px;
  z-index: 2100;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.assistant-launcher {
  width: 64px;
  height: 64px;
  min-width: 64px;
  padding: 0;
  border: none;
  border-radius: 50%;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #4f8df7, #2f6fed);
  box-shadow: 0 18px 35px rgba(28, 72, 173, 0.32);
}

.assistant-launcher-label {
  padding: 6px 12px;
  border-radius: 999px;
  background: rgba(15, 23, 42, 0.86);
  color: #fff;
  font-size: 12px;
  letter-spacing: 0.04em;
  backdrop-filter: blur(12px);
}

.assistant-panel {
  height: 100%;
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 4px 0 8px;
}

.assistant-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.assistant-title {
  font-size: 18px;
  font-weight: 700;
  color: #0f172a;
}

.assistant-subtitle {
  margin-top: 6px;
  font-size: 12px;
  color: #64748b;
  line-height: 1.6;
}

.assistant-tip {
  border-radius: 14px;
}

.assistant-shortcuts {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.assistant-tag {
  cursor: pointer;
  user-select: none;
}

.assistant-messages {
  flex: 1;
  min-height: 320px;
  border-radius: 18px;
  background: linear-gradient(180deg, rgba(248, 250, 252, 0.92), rgba(241, 245, 249, 0.96));
  padding: 16px;
  border: 1px solid rgba(148, 163, 184, 0.18);
}

.message-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.message-row {
  display: flex;
}

.message-row.is-assistant {
  justify-content: flex-start;
}

.message-row.is-user {
  justify-content: flex-end;
}

.message-bubble {
  max-width: 84%;
  padding: 12px 14px;
  border-radius: 16px;
  box-shadow: 0 8px 24px rgba(15, 23, 42, 0.08);
}

.message-row.is-assistant .message-bubble {
  background: #ffffff;
  color: #0f172a;
}

.message-row.is-user .message-bubble {
  background: linear-gradient(135deg, #2563eb, #3b82f6);
  color: #fff;
}

.message-role {
  margin-bottom: 6px;
  font-size: 12px;
  opacity: 0.72;
}

.message-content {
  font-size: 14px;
  line-height: 1.75;
  white-space: pre-wrap;
  word-break: break-word;
}

.assistant-composer {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.composer-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.composer-hint {
  font-size: 12px;
  color: #94a3b8;
}

:deep(.assistant-drawer .el-drawer__body) {
  padding: 18px 18px 20px;
}

@media (max-width: 768px) {
  .assistant-launcher-wrap {
    right: 16px;
    bottom: 16px;
  }

  :deep(.assistant-drawer) {
    width: min(100vw, 100% - 16px) !important;
  }
}
</style>
