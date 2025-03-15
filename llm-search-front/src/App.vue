<script setup>
import { ref } from 'vue'
import axios from 'axios'

const count = ref(0);
const search = ref('');
const loading = ref(false);
const results = ref(null);
const error = ref(null);
const host = 'http://localhost:5000';

const searchInput = () => {
  console.log(search.value);
}

function sendQuery() {
  if (!search.value.trim()) {
    console.log('Search is empty');
    return;
  }
  
  loading.value = true;
  error.value = null;
  
  console.log('Sending query:', search.value);
  
  axios.post(host + '/api/query', {
    query: search.value
  })
    .then(response => {
      results.value = response.data.result;
      console.log('Search results:', results.value);
    })
    .catch(err => {
      // TODO: Comprobar
      error.value = err.message || 'Error al realizar la búsqueda';
      console.error('Error performing search:', err);
    })
    .finally(() => {
      loading.value = false;
      search.value = '';
    })
}
</script>

<template>
  <div class="flex flex-col h-screen justify-center items-center bg-black p-10">
    
    <div class="h-full flex items-center w-full">
      <div class="flex flex-col">
        <h1 class="bg-gradient-to-r from-pink-500 to-violet-500 bg-clip-text text-5xl font-extrabold text-transparent">Meow</h1>
        <p class="neon-text ps-1">Neko ฅ⁠^⁠•⁠ﻌ⁠•⁠^⁠ฅ</p>
        <p class="ps-1 text-white">Count is: {{ count }}</p>
      </div>
    </div>
    
    <div class="ring-2 ring-blue-500 p-2 rounded-lg">
      <div class="flex items-center">
        <input 
          type="text" 
          v-model="search" 
          @input="searchInput"
          @keyup.enter="sendQuery" 
          placeholder="Search..."
          class="p-2 text-2xl bg-black text-white border-b-2 border-white focus:outline-none focus:border-pink-500 transition-colors duration-300 w-64"
        >
        <button 
          @click="sendQuery"
          class="ml-2 bg-gradient-to-r from-pink-500 to-violet-500 text-white px-3 py-1 rounded-lg hover:opacity-90 transition-opacity"
          :disabled="loading"
        >
          <span v-if="!loading">Buscar</span>
          <span v-else>...</span>
        </button>
      </div>
      
      <!-- Loading and Error states -->
      <div v-if="loading" class="mt-2 text-blue-400">Waiting...</div>
      <div v-if="error" class="mt-2 text-red-500">{{ error }}</div>
      
      <!-- Result -->
      <div v-if="results" class="mt-2">
        <p class="text-green-500">Result: {{ results }}</p>
      </div>
    </div>
    
  </div>

  <div class="absolute bottom-0 right-0 p-4">
    <button 
      @click="count++" 
      class="flex size-10 animate-bounce items-center justify-center rounded-full bg-white p-2 ring-1 ring-gray-900/5 dark:bg-white/5 dark:ring-white/20 hover:bg-white/10 hover:ring-white/20 duration-150"
      aria-label="Increment count"
    >
      <svg class="size-6 text-violet-500" fill="none" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" viewBox="0 0 24 24" stroke="currentColor">
        <path d="M19 14l-7 7m0 0l-7-7m7 7V3"></path>
      </svg>
    </button>
  </div>
</template>

<style>
@keyframes colorChange {
  0% { color: #ff00ff; text-shadow: 0 0 10px #ff00ff, 0 0 20px #ff00ff, 0 0 30px #ff00ff; }
  25% { color: #00ffff; text-shadow: 0 0 10px #00ffff, 0 0 20px #00ffff, 0 0 30px #00ffff; }
  50% { color: #ffff00; text-shadow: 0 0 10px #ffff00, 0 0 20px #ffff00, 0 0 30px #ffff00; }
  75% { color: #00ff00; text-shadow: 0 0 10px #00ff00, 0 0 20px #00ff00, 0 0 30px #00ff00; }
  100% { color: #ff00ff; text-shadow: 0 0 10px #ff00ff, 0 0 20px #ff00ff, 0 0 30px #ff00ff; }
}

.neon-text {
  animation: colorChange 8s infinite;
  filter: brightness(1.1);
  color: #ff00ff;
}
</style>