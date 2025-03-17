<template>
  <div class="min-h-screen w-full overflow-hidden bg-gradient-to-b from-zinc-900 via-zinc-900 to-zinc-950 dark">
    <!-- Config button -->
    <div class="fixed top-4 right-4 z-10">
      <button
        @click="isSettingsOpen = true"
        class="rounded-full h-10 w-10 bg-zinc-800/80 backdrop-blur-lg border border-zinc-700/50 shadow-lg hover:bg-zinc-700/80 transition-all duration-300 hover:scale-105 flex items-center justify-center"
      >
        <Settings class="h-5 w-5 text-zinc-300" />
        <span class="sr-only">Open settings</span>
      </button>
      
      <!-- Settings panel -->
      <Teleport to="body">
        <Transition name="fade">
          <div v-if="isSettingsOpen" class="fixed inset-0 bg-black/50 z-50 flex justify-end" @click.self="isSettingsOpen = false">
            <Transition name="slide">
              <div v-if="isSettingsOpen" class="w-80 bg-zinc-900 border-l border-zinc-800 text-white h-full p-6">
                <div class="space-y-6">
                  <div class="flex items-center gap-2">
                    <div class="h-8 w-8 rounded-full bg-gradient-to-br from-violet-600 to-indigo-600 flex items-center justify-center">
                      <Settings class="h-4 w-4 text-white" />
                    </div>
                    <h2 class="text-lg font-semibold text-white">Configuration</h2>
                  </div>
                  <div class="h-px bg-zinc-800 w-full"></div>

                  <div class="space-y-5">
                    <div class="flex items-center justify-between">
                      <label for="dark-mode" class="text-zinc-200">Dark Mode</label>
                      <input type="checkbox" id="dark-mode" v-model="darkMode" class="toggle" />
                    </div>

                    <div class="flex items-center justify-between">
                      <label for="notifications" class="text-zinc-200">Notifications</label>
                      <input type="checkbox" id="notifications" class="toggle" />
                    </div>

                    <div class="flex items-center justify-between">
                      <label for="sound" class="text-zinc-200">Sound Effects</label>
                      <input type="checkbox" id="sound" class="toggle" />
                    </div>

                    <div class="space-y-2">
                      <label for="model" class="text-zinc-200">AI Model</label>
                      <select id="model" class="w-full rounded-md border border-zinc-800 bg-zinc-950 px-3 py-2 text-white">
                        <option value="gpt-3.5">GPT-3.5</option>
                        <option value="gpt-4">GPT-4</option>
                        <option value="claude">Claude</option>
                      </select>
                    </div>

                    <div class="space-y-2">
                      <label for="temperature" class="text-zinc-200">Temperature</label>
                      <input
                        id="temperature"
                        type="range"
                        min="0"
                        max="1"
                        step="0.1"
                        v-model="temperature"
                        class="w-full accent-violet-500"
                      />
                      <div class="flex justify-between text-xs text-zinc-400">
                        <span>Precise</span>
                        <span>Creative</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </Transition>
          </div>
        </Transition>
      </Teleport>
    </div>

    <!-- Main chat area with centered content -->
    <div class="flex flex-1 flex-col items-center pt-4 pb-28">
      <div class="w-full max-w-3xl flex flex-col h-full px-4">
        <!-- Messages area -->
        <div class="flex-1 overflow-y-auto py-6 space-y-6">
          <TransitionGroup name="message">
            <div 
              v-for="message in messages" 
              :key="message.id" 
              :class="`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`"
            >
              <div
                :class="`flex gap-3 max-w-[80%] ${message.sender === 'user' ? 'flex-row-reverse' : 'flex-row'}`"
              >
              <div
                :class="`h-9 w-9 min-h-[2.25rem] min-w-[2.25rem] flex-shrink-0 rounded-full flex items-center justify-center ${
                  message.sender === 'assistant'
                    ? 'border-2 border-violet-500 bg-gradient-to-br from-violet-600 to-indigo-600'
                    : 'bg-gradient-to-br from-emerald-500 to-teal-500'
                }`"
              >
                <div class="text-white flex items-center justify-center">
                  <User v-if="message.sender === 'user'" class="h-4 w-4 min-h-[1rem] min-w-[1rem] flex-shrink-0" />
                  <Bot v-else class="h-4 w-4 min-h-[1rem] min-w-[1rem] flex-shrink-0" />
                </div>
              </div>
                <div
                  :class="`rounded-2xl p-4 ${
                    message.sender === 'user'
                      ? 'bg-gradient-to-br from-emerald-500/90 to-teal-600/90 text-white shadow-lg shadow-emerald-500/10'
                      : 'bg-zinc-800/80 border border-zinc-700/50 shadow-lg shadow-violet-500/5 text-white'
                  }`"
                >
                  <div v-if="message.id === typingMessageId" class="typing-indicator">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                  <template v-else>{{ message.content }}</template>
                </div>
              </div>
            </div>
          </TransitionGroup>
        </div>
      </div>
    </div>

    <!-- Copilot-style input area - fixed at bottom -->
    <div class="fixed bottom-0 left-0 right-0 py-6 bg-transparent flex justify-center">
      <div class="w-full max-w-3xl px-4">
        <div class="relative">
          <div class="relative flex items-center bg-zinc-900/90 backdrop-blur-xl rounded-xl shadow-2xl border border-zinc-700/50 transition-all duration-300 hover:border-zinc-600/70 focus-within:border-zinc-600/70">
            <input
              v-model="inputValue"
              @keyup.enter="handleSendMessage"
              @focus="inputFocused = true"
              @blur="inputFocused = false"
              placeholder="Ask me anything..."
              class="flex-1 border-0 bg-transparent focus:outline-none text-white placeholder:text-zinc-400 text-base py-6 pl-6 pr-2 h-auto"
            />
            <div class="pr-4 flex items-center">
              <button
                @click="handleSendMessage"
                class="h-10 w-10 rounded-full bg-zinc-800 hover:bg-violet-600 transition-all duration-300 hover:scale-105 flex items-center justify-center"
              >
                <Send class="h-5 w-5 text-zinc-300" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue';
import { Settings, Send, Bot, User } from 'lucide-vue-next';

// State
const messages = ref([
  {
    id: "1",
    content: "Hello! How can I help you today?",
    sender: "assistant",
    timestamp: new Date(),
  }
]);
const inputValue = ref("");
const isSettingsOpen = ref(false);
const darkMode = ref(true);
const temperature = ref(0.7);
const inputFocused = ref(false);
const typingMessageId = ref(null);

// Enable dark mode on component mount
onMounted(() => {
  document.documentElement.classList.add("dark");
});

// Function to handle sending a new message
const handleSendMessage = async () => {
  if (inputValue.value.trim() === "") return;
  
  // Add user message
  const userMessage = {
    id: Date.now().toString(),
    content: inputValue.value,
    sender: "user",
    timestamp: new Date(),
  };
  
  messages.value.push(userMessage);
  
  // Clear input
  inputValue.value = "";
  
  // Add typing indicator
  const typingId = (Date.now() + 1).toString();
  await nextTick();
  
  messages.value.push({
    id: typingId,
    content: "",
    sender: "assistant",
    timestamp: new Date(),
  });
  
  typingMessageId.value = typingId;
  
  // Simulate assistant response after delay
  setTimeout(() => {
    typingMessageId.value = null;
    
    // Find and update the typing message
    const index = messages.value.findIndex(m => m.id === typingId);
    if (index !== -1) {
      messages.value[index].content = `I received your message: "${userMessage.content}"`;
    }
  }, 1500);
};
</script>

<style scoped>
/* Custom toggle switch styling */
.toggle {
  position: relative;
  display: inline-block;
  width: 40px;
  height: 20px;
  appearance: none;
  background-color: #374151;
  border-radius: 20px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.toggle:checked {
  background-color: #8b5cf6;
}

.toggle::before {
  content: "";
  position: absolute;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  top: 2px;
  left: 2px;
  background-color: white;
  transition: transform 0.3s;
}

.toggle:checked::before {
  transform: translateX(20px);
}

/* Typing indicator animation */
.typing-indicator {
  display: flex;
  align-items: center;
  column-gap: 4px;
  height: 20px;
}

.typing-indicator span {
  display: block;
  width: 8px;
  height: 8px;
  background-color: rgba(255, 255, 255, 0.7);
  border-radius: 50%;
  animation: typing 1s infinite ease-in-out;
}

.typing-indicator span:nth-child(1) {
  animation-delay: 0s;
}

.typing-indicator span:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-indicator span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes typing {
  0%, 60%, 100% {
    transform: translateY(0);
    opacity: 0.6;
  }
  30% {
    transform: translateY(-4px);
    opacity: 1;
  }
}

/* Message animations */
.message-enter-active,
.message-leave-active {
  transition: all 0.3s ease;
}

.message-enter-from {
  opacity: 0;
  transform: translateY(20px);
}

.message-leave-to {
  opacity: 0;
  transform: translateY(-20px);
}

/* Fade transition */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* Slide transition */
.slide-enter-active,
.slide-leave-active {
  transition: transform 0.3s ease;
}

.slide-enter-from,
.slide-leave-to {
  transform: translateX(100%);
}
</style>