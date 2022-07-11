import type { Ref } from "vue"
import { ref, unref, watch } from "vue"
import { useRafFn } from "@vueuse/core"

export interface Paddle {
  x: number
  y: number
  width: number
  height: number
  dy: number
  color: string
}

export interface Ball {
  x: number
  y: number
  radius: number
  dx: number
  dy: number
  color: string
}

export type GameState = "playing" | "gameover" | "paused"

export interface UsePingPongParams {
  context: Ref<CanvasRenderingContext2D | undefined>
  ballMaxSpeed: number
  paddleMaxSpeed: number
  leftPaddleSpeedPercent: Ref<number>
  rightPaddleSpeedPercent: Ref<number>
  paddleWidth: number
  paddleHeight: number
  ballRadius: number
  ballColor: string
  leftPaddleColor: string
  rightPaddleColor: string
}

export function usePingPong({
  context: contextRef,
  ballMaxSpeed,
  paddleMaxSpeed,
  leftPaddleSpeedPercent,
  rightPaddleSpeedPercent,
  paddleWidth,
  paddleHeight,
  ballRadius,
  ballColor,
  leftPaddleColor,
  rightPaddleColor,
}: UsePingPongParams) {
  const gameState = ref<GameState>("paused")
  const scoreLeft = ref(0)
  const scoreRight = ref(0)

  const ball = {
    x: 0,
    y: 0,
    radius: ballRadius,
    dx: 0,
    dy: 0,
    color: ballColor,
  }
  const leftPaddle = {
    x: 0,
    y: 0,
    width: paddleWidth,
    height: paddleHeight,
    dy: 0,
    color: leftPaddleColor,
  }
  const rightPaddle = {
    x: 0,
    y: 0,
    width: paddleWidth,
    height: paddleHeight,
    dy: 0,
    color: rightPaddleColor,
  }

  const pause = () => {
    gameState.value = "paused"
  }
  const resume = () => {
    gameState.value = "playing"
  }
  const reset = () => {
    const context = unref(contextRef)

    if (!context) {
      return
    }

    scoreLeft.value = 0
    scoreRight.value = 0
    gameState.value = "paused"

    ball.x = context.canvas.width / 2
    ball.y = context.canvas.height / 2
    const randomDirectionX = Math.random() < 0.5 ? -1 : 1
    const randomDirectionY = Math.random() < 0.5 ? -1 : 1
    const randomSpeedY = Math.min(1, Math.random() + 0.5) * ballMaxSpeed
    ball.dx = randomDirectionX * ballMaxSpeed
    ball.dy = randomDirectionY * randomSpeedY

    const paddleCenterY = context.canvas.height / 2 - paddleHeight / 2
    leftPaddle.y = paddleCenterY
    rightPaddle.y = paddleCenterY
    leftPaddle.x = 0
    rightPaddle.x = context.canvas.width - paddleWidth
    leftPaddle.dy = 0
    rightPaddle.dy = 0
  }

  const { pause: pauseRaf, resume: resumeRaf } = useRafFn(() => {
    const context = unref(contextRef)

    if (!context) {
      return
    }

    context.clearRect(0, 0, context.canvas.width, context.canvas.height)

    leftPaddle.dy = leftPaddleSpeedPercent.value * paddleMaxSpeed
    rightPaddle.dy = rightPaddleSpeedPercent.value * paddleMaxSpeed

    // Move & draw paddles
    movePaddle(leftPaddle, context)
    movePaddle(rightPaddle, context)
    drawPaddle(leftPaddle, context)
    drawPaddle(rightPaddle, context)

    // Move & draw ball
    const ballGoneTo = moveBallAndCheckIfGone(
      ball,
      context,
      leftPaddle,
      rightPaddle,
      ballMaxSpeed,
      paddleMaxSpeed
    )
    drawBall(ball, context)

    if (ballGoneTo) {
      if (ballGoneTo === "to-left") {
        scoreRight.value++
      } else {
        scoreLeft.value++
      }
      gameState.value = "gameover"
    }
  })
  
  watch(gameState, (newState) => {
    if (newState === "gameover" || newState === "paused") {
      pauseRaf()
    } else if (newState === "playing") {
      resumeRaf()
    }
  }, { immediate: true })

  return {
    gameState,
    scoreLeft,
    scoreRight,
    pause,
    resume,
    reset,
  }
}

function movePaddle(paddle: Paddle, context: CanvasRenderingContext2D) {
  paddle.y += paddle.dy

  if (paddle.y < 0) {
    paddle.y = 0
  } else {
    const yMax = context.canvas.height - paddle.height
    if (paddle.y > yMax) {
      paddle.y = yMax
    }
  }
}

function drawPaddle(paddle: Paddle, context: CanvasRenderingContext2D) {
  context.fillStyle = paddle.color
  context.fillRect(paddle.x, paddle.y, paddle.width, paddle.height)
}

function moveBallAndCheckIfGone(
  ball: Ball,
  context: CanvasRenderingContext2D,
  leftPaddle: Paddle,
  rightPaddle: Paddle,
  ballMaxSpeed: number,
  paddleMaxSpeed: number
): "to-left" | "to-right" | false {
  ball.x += ball.dx
  ball.y += ball.dy

  // Check if ball is gone
  if (ball.x - ball.radius <= 0) {
    return "to-left"
  } else if (ball.x + ball.radius >= context.canvas.width) {
    return "to-right"
  }

  // Pong ball vertically
  if (ball.y + ball.radius > context.canvas.height) {
    ball.y = context.canvas.height - ball.radius
    ball.dy = -ball.dy
  } else if (ball.y - ball.radius < 0) {
    ball.y = ball.radius
    ball.dy = -ball.dy
  }

  // Pong ball horizontally
  if (areBallAndPaddleCollide(ball, leftPaddle)) {
    ball.x = leftPaddle.x + leftPaddle.width + ball.radius
    ball.dx = -ball.dx
    adjustBallVerticalSpeed(ball, leftPaddle, ballMaxSpeed, paddleMaxSpeed)
  } else if (areBallAndPaddleCollide(ball, rightPaddle)) {
    ball.x = rightPaddle.x - ball.radius
    ball.dx = -ball.dx
    adjustBallVerticalSpeed(ball, rightPaddle, ballMaxSpeed, paddleMaxSpeed)
  }

  return false
}

function drawBall(ball: Ball, context: CanvasRenderingContext2D) {
  context.beginPath()
  context.arc(ball.x, ball.y, ball.radius, 0, Math.PI * 2)
  context.fillStyle = ball.color
  context.fill()
  context.closePath()
}

const areBallAndPaddleCollide = (ball: Ball, paddle: Paddle) => (
  ball.x - ball.radius < paddle.x + paddle.width &&
  ball.x + ball.radius > paddle.x &&
  ball.y - ball.radius < paddle.y + paddle.height &&
  ball.y + ball.radius > paddle.y
)

function adjustBallVerticalSpeed(
  ball: Ball,
  bouncedPaddle: Paddle,
  ballMaxSpeed: number,
  paddleMaxSpeed: number
) {
  const paddleSpeedPercent = bouncedPaddle.dy / paddleMaxSpeed
  const adjacment = ballMaxSpeed * paddleSpeedPercent * Math.random() * 0.2

  ball.dy += adjacment
  if (ball.dy > ballMaxSpeed) {
    ball.dy = ballMaxSpeed
  } else if (ball.dy < -ballMaxSpeed) {
    ball.dy = -ballMaxSpeed
  }
}
