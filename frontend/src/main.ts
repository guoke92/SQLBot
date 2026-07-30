import 'core-js/features/object/has-own'
// @ts-expect-error: css-has-pseudo/browser lacks official type definitions
import cssHasPseudo from 'css-has-pseudo/browser'

import { createApp } from 'vue'
import './style.less'
import App from './App.vue'
import router from './router'
import { i18n } from './i18n'
import VueDOMPurifyHTML from 'vue-dompurify-html'
import { setupStore } from './stores'

// import 'element-plus/dist/index.css'
cssHasPseudo(document)

function supportsFlexGap() {
  const flex = document.createElement('div')
  flex.style.display = 'flex'
  flex.style.flexDirection = 'column'
  flex.style.rowGap = '1px'

  flex.appendChild(document.createElement('div'))
  flex.appendChild(document.createElement('div'))

  document.body.appendChild(flex)
  const isSupported = flex.scrollHeight === 1
  document.body.removeChild(flex)

  return isSupported
}

document.documentElement.setAttribute('data-no-flex-gap', String(!supportsFlexGap()))

const app = createApp(App)

setupStore(app)
app.use(router)
app.use(i18n)
app.use(VueDOMPurifyHTML)
app.mount('#app')
