/**
 * Single owner of chat message-list auto-scroll.
 *
 * Policy (no continuous sticky interval during stream):
 * - force: page init / history switch / user just sent a message
 * - lifecycle: answer finish / content ready — only if user is still near bottom
 *
 * Scroll-away pauses auto-scroll until the user returns near bottom or force is called.
 * Replaces the former setInterval(scrollBottom, 300) + dual scrollToBottom/scrollBottom paths.
 */
import { nextTick, onBeforeUnmount, type Ref } from 'vue'

export type ChatScrollOptions = {
  /** Distance from bottom (px) still treated as "near bottom". Default 80. */
  nearBottomPx?: number
}

type ElScrollbarLike = {
  wrapRef?: HTMLElement
  setScrollTop?: (top: number) => void
  scrollTo?: (options: ScrollToOptions) => void
}

export function useChatScroll(
  scrollRef: Ref<ElScrollbarLike | undefined | null>,
  contentRef: Ref<HTMLElement | undefined | null>,
  options: ChatScrollOptions = {}
) {
  const nearBottomPx = options.nearBottomPx ?? 80

  let userScrolledAway = false
  let programmatic = false
  let programmaticClearTimer: ReturnType<typeof setTimeout> | undefined
  let smoothRaf: number | undefined

  function getWrap(): HTMLElement | undefined {
    return scrollRef.value?.wrapRef
  }

  function isNearBottom(): boolean {
    const wrap = getWrap()
    if (!wrap) {
      return true
    }
    const distance = wrap.scrollHeight - wrap.scrollTop - wrap.clientHeight
    return distance <= nearBottomPx
  }

  function markProgrammatic(durationMs = 450) {
    programmatic = true
    if (programmaticClearTimer !== undefined) {
      clearTimeout(programmaticClearTimer)
    }
    programmaticClearTimer = setTimeout(() => {
      programmatic = false
      programmaticClearTimer = undefined
    }, durationMs)
  }

  function applyScrollTop(top: number, smooth: boolean) {
    const inst = scrollRef.value
    const wrap = getWrap()
    if (!inst && !wrap) {
      return
    }
    markProgrammatic(smooth ? 500 : 120)
    if (smooth && typeof inst?.scrollTo === 'function') {
      inst.scrollTo({ top, behavior: 'smooth' })
      return
    }
    if (typeof inst?.setScrollTop === 'function') {
      inst.setScrollTop(top)
      return
    }
    if (wrap) {
      wrap.scrollTo({ top, behavior: smooth ? 'smooth' : 'auto' })
    }
  }

  function scrollToLatest(opts: { force?: boolean; smooth?: boolean } = {}) {
    const force = !!opts.force
    const smooth = opts.smooth !== false
    if (!force && userScrolledAway) {
      return
    }
    nextTick(() => {
      if (!force && userScrolledAway) {
        return
      }
      const content = contentRef.value
      const wrap = getWrap()
      const top = content?.clientHeight ?? wrap?.scrollHeight ?? 0
      if (force) {
        userScrolledAway = false
      }
      applyScrollTop(top, smooth)
      // Chart/DOM may grow one frame later after finish handlers.
      if (smoothRaf !== undefined) {
        cancelAnimationFrame(smoothRaf)
      }
      smoothRaf = requestAnimationFrame(() => {
        const content2 = contentRef.value
        const wrap2 = getWrap()
        const top2 = content2?.clientHeight ?? wrap2?.scrollHeight ?? 0
        if (force || !userScrolledAway) {
          applyScrollTop(top2, false)
        }
        smoothRaf = undefined
      })
    })
  }

  /** Init / history / send — always jump to latest. */
  function forceScrollToBottom(smooth = true) {
    scrollToLatest({ force: true, smooth })
  }

  /** Finish / content-ready — only if user hasn't scrolled away. */
  function maybeScrollToBottom(smooth = true) {
    scrollToLatest({ force: false, smooth })
  }

  /** el-scrollbar @scroll handler. */
  function handleScroll(_val?: { scrollTop?: number }) {
    if (programmatic) {
      return
    }
    if (isNearBottom()) {
      userScrolledAway = false
    } else {
      userScrolledAway = true
    }
  }

  onBeforeUnmount(() => {
    if (programmaticClearTimer !== undefined) {
      clearTimeout(programmaticClearTimer)
    }
    if (smoothRaf !== undefined) {
      cancelAnimationFrame(smoothRaf)
    }
  })

  return {
    handleScroll,
    forceScrollToBottom,
    maybeScrollToBottom,
    isNearBottom: () => isNearBottom(),
    /** Read-only snapshot for rare callers; prefer force/maybe APIs. */
    hasScrolledAway: () => userScrolledAway,
  }
}

export default useChatScroll
