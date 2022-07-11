<script setup lang="ts">
import { ref, onMounted } from "vue"
import { usePingPong } from "@/composables/usePingPong"

const canvas = ref<HTMLCanvasElement>()
const wrapper = ref<HTMLDivElement>()
const context = ref<CanvasRenderingContext2D>()
const leftPaddleSpeedPercent = ref(0)
const rightPaddleSpeedPercent = ref(0)
const {
  gameState,
  scoreLeft,
  scoreRight,
  pause,
  resume,
  reset
} = usePingPong({
  context,
  ballMaxSpeed: 8,
  paddleMaxSpeed: 12,
  leftPaddleSpeedPercent,
  rightPaddleSpeedPercent,
  paddleWidth: 24,
  paddleHeight: 128,
  ballRadius: 16,
  ballColor: "white",
  leftPaddleColor: "grey",
  rightPaddleColor: "grey",
})

window.addEventListener("keydown", (event) => {
  switch (event.key) {
    case "ArrowUp":
      rightPaddleSpeedPercent.value = -1
      break
    case "ArrowDown":
      rightPaddleSpeedPercent.value = 1
      break
    case "w":
      leftPaddleSpeedPercent.value = -1
      break
    case "s":
      leftPaddleSpeedPercent.value = 1
      break
    case " ":
      if (gameState.value === "paused") {
        resume()
      } else {
        pause()
      }
      break
    case "r":
      reset()
      resume()
      break
  }
})

window.addEventListener("keyup", (event) => {
  switch (event.key) {
    case "ArrowUp":
      rightPaddleSpeedPercent.value = 0
      break
    case "ArrowDown":
      rightPaddleSpeedPercent.value = 0
      break
    case "w":
      leftPaddleSpeedPercent.value = 0
      break
    case "s":
      leftPaddleSpeedPercent.value = 0
      break
  }
})

onMounted(() => {
  if (!canvas.value) {
    console.error("canvas is null")
    return
  }

  if (!wrapper.value) {
    console.error("wrapper is null")
    return
  }

  canvas.value.height = wrapper.value.clientHeight
  canvas.value.width = wrapper.value.clientWidth

  const ctxt = canvas.value.getContext("2d")

  if (!ctxt) {
    console.error("context is null")
    return
  }

  context.value = ctxt
  reset()
  resume()
})
</script>

<template>
  <div ref="wrapper" class="canvas-wrapper">
    <div class="score-container">
      <span class="score score-left">{{ scoreLeft ?? "–" }}</span>
      <span class="score score-right">{{ scoreRight ?? "–" }}</span>
    </div>
    <canvas ref="canvas" class="canvas"></canvas>
  </div>
</template>

<style>
.canvas-wrapper {
  margin: 0;
  position: absolute;
  left: 0;
  right: 0;
  bottom: 0;
  width: 100%;
  height: 100%;
  top: 0;
  background: #000;
  overflow: hidden;
}

.canvas {
}

.score-container {
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  justify-content: center;
  align-items: center;
  margin: auto;
  width: 100%;
  font-weight: bold;
  opacity: 0.25;
  gap: 64px;
  font-size: 64px;
  color: #fff;
}

/* .score {
  color: #fff;
  font-size: 32px;
  font-weight: bold;
} */
</style>
