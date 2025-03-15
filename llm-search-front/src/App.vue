<script setup>
import { ref } from 'vue';

// Set up animation control
const isAnimating = ref(true);
</script>

<template>
  <div class="flex justify-center items-center h-screen bg-black">
    <h1 class="text-center font-bold text-6xl neon-text ">Meow</h1>
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
}
</style>