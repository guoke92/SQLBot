<script lang="ts" setup>
import { computed } from 'vue'
import { ElMenu } from 'element-plus-secondary'
import 'element-plus-secondary/es/components/menu/style/css'
import { useRoute, useRouter } from 'vue-router'
import MenuItem from './MenuItem.vue'
import { useUserStore } from '@/stores/user'
import { getMainNavigation, getSystemNavigation } from '@/router/navigation'
const userStore = useUserStore()
const router = useRouter()
defineProps({
  collapse: Boolean,
})

const route = useRoute()
const activeMenu = computed(() => route.path)
const showSysmenu = computed(() => {
  return route.path.includes('/system')
})

const routerList = computed(() => {
  if (showSysmenu.value) {
    return getSystemNavigation(router)
  }
  return getMainNavigation(router, {
    isAdmin: userStore.isAdmin,
    isSpaceAdmin: userStore.isSpaceAdmin,
  })
})
</script>

<template>
  <el-menu :default-active="activeMenu" class="el-menu-demo ed-menu-vertical" :collapse="collapse">
    <MenuItem v-for="menu in routerList" :key="menu.path" :menu="menu"></MenuItem>
  </el-menu>
</template>

<style lang="less">
.ed-menu-vertical {
  --ed-menu-item-height: 40px;
  --ed-menu-bg-color: transparent;
  --ed-menu-base-level-padding: 4px;
  border-right: none;
  width: 100%;

  .menu-item-label {
    min-width: 0;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .ed-menu-item {
    height: 40px !important;
    border-radius: 6px !important;
    margin-bottom: 2px;
    &.is-active {
      background-color: #fff !important;
      border-radius: 6px;
      font-weight: 500;
    }
  }

  .ed-sub-menu .ed-sub-menu__title {
    border-radius: 6px;
  }

  .ed-sub-menu.is-active:not(.is-opened) {
    .ed-sub-menu__title {
      background-color: #fff !important;
      color: var(--ed-color-primary) !important;
      font-weight: 500;
    }
  }

  .ed-sub-menu.is-active.is-opened {
    .ed-sub-menu__title {
      color: var(--ed-color-primary) !important;
      font-weight: 500;
    }
  }

  .ed-sub-menu .ed-icon {
    margin-right: 8px;
  }
}
.ed-popper.is-light:has(.ed-menu--popup) {
  border: 1px solid #dee0e3;
  border-radius: 6px;
  box-shadow: 0px 4px 8px 0px #1f23291a;
  background: #eff1f0;
  overflow: hidden;
}
.ed-menu--popup {
  padding: 8px;
  background: #eff1f0;

  .ed-menu-item {
    padding: 9px 16px;
    height: 40px !important;
    border-radius: 6px;
    &.is-active {
      background-color: #fff !important;
      font-weight: 500;
    }
  }
}
.sub-menu-popup-title {
  display: none;
}

.ed-menu--popup-container .sub-menu-popup-title {
  display: block;
  padding: 8px 16px;
  color: #646a73 !important;
  font-size: 12px;
  line-height: 20px;
  list-style: none;
  pointer-events: none;
}
</style>
