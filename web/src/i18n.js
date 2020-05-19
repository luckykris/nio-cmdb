import Vue from 'vue/dist/vue.js'
import VueI18n from 'vue-i18n'
Vue.use(VueI18n)
const messages = {
  en: {
    content: {
      add: 'add',
      update: 'update',
      delete: 'delete',
      search: 'search'
    }
  },
  cn: {
    content: {
      add: '增加',
      update: '更新',
      delete: '删除',
      search: '查询'
    }
  }
}
export const i18n = new VueI18n({
  locale: 'cn', // set locale
  fallbackLocale: 'cn', // set fallback locale
  messages // set locale messages
})
