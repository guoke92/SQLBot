<script lang="ts">
import { h, defineComponent, type Component, type PropType, type VNodeChild } from 'vue'
import { ElMenuItem, ElSubMenu, ElIcon } from 'element-plus-secondary'
import { useRouter, useRoute } from 'vue-router'
import chat from '@/assets/svg/menu/icon_chat_filled.svg'
import noChat from '@/assets/svg/menu/icon_chat_outlined.svg'
import dashboard from '@/assets/svg/menu/icon_dashboard_filled.svg'
import { useEmitt } from '@/utils/useEmitt'
import noDashboard from '@/assets/svg/menu/icon_dashboard_outlined.svg'
import ds from '@/assets/svg/menu/icon_database_filled.svg'
import noDs from '@/assets/svg/menu/icon_database_outlined.svg'
import model from '@/assets/svg/menu/icon_dataset_filled.svg'
import noModel from '@/assets/svg/menu/icon_dataset_outlined.svg'
import embedded from '@/assets/svg/menu/icon_embedded_filled.svg'
import noEmbedded from '@/assets/svg/menu/icon_embedded_outlined.svg'
import user from '@/assets/svg/menu/icon_member_filled.svg'
import noUser from '@/assets/svg/menu/icon_member_outlined.svg'
import workspace from '@/assets/svg/menu/icon_moments-categories_filled.svg'
import noWorkspace from '@/assets/svg/menu/icon_moments-categories_outlined.svg'
import set from '@/assets/svg/menu/icon_setting_filled.svg'
import noSet from '@/assets/svg/menu/icon-setting.svg'
import log from '@/assets/svg/menu/icon_log_filled.svg'
import noLog from '@/assets/svg/menu/icon_log_outlined.svg'
import type { NavigationRoute } from '@/router/navigation'

const iconMap = {
  chat,
  noChat,
  ds,
  noDs,
  dashboard,
  noDashboard,
  workspace,
  noWorkspace,
  set,
  noSet,
  user,
  noUser,
  model,
  noModel,
  embedded,
  noEmbedded,
  log,
  noLog,
}

type MenuIconName = keyof typeof iconMap

const resolveIcon = (name: unknown): Component | undefined => {
  if (typeof name !== 'string' || !(name in iconMap)) {
    return undefined
  }
  return iconMap[name as MenuIconName] as unknown as Component
}

const renderIcon = (name: unknown): VNodeChild => {
  const icon = resolveIcon(name)
  if (!icon) {
    return null
  }
  return h(ElIcon, { size: 18 }, { default: () => h(icon) })
}

const renderLabel = (title: unknown) => h('span', { class: 'menu-item-label' }, String(title ?? ''))

const MenuItem = defineComponent({
  name: 'MenuItem',
  props: {
    menu: {
      type: Object as PropType<NavigationRoute>,
      required: true,
    },
  },
  setup(props) {
    const router = useRouter()
    const route = useRoute()
    const { emitter } = useEmitt()

    const navigate = (path: string) => {
      if (path === '/ds/index') {
        emitter.emit('ds-index-click')
      }
      void router.push(path)
    }

    return () => {
      const { children, hidden, path, meta } = props.menu
      if (hidden || meta.hidden) {
        return null
      }

      if (children?.length) {
        const { title, iconDeActive, iconActive } = meta
        const icon =
          route.path === path || route.path.startsWith(`${path}/`) ? iconActive : iconDeActive
        return h(
          ElSubMenu,
          { index: path },
          {
            title: () => [renderIcon(icon), renderLabel(title)],
            default: () => [
              h(
                'li',
                {
                  class: 'sub-menu-popup-title',
                  role: 'presentation',
                  'aria-hidden': 'true',
                },
                String(title ?? '')
              ),
              ...children.map((child) => h(MenuItem, { key: child.path, menu: child })),
            ],
          }
        )
      }

      const { title, iconDeActive, iconActive } = meta
      const icon = route.path === path ? iconActive : iconDeActive
      return h(
        ElMenuItem,
        { index: path, onClick: () => navigate(path) },
        {
          default: () => [renderIcon(icon), renderLabel(title)],
        }
      )
    }
  },
})
export default MenuItem
</script>
