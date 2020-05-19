import { getAttributeType, getResourceDefined } from '@/api/resource'

const state = {
  attributeType: [],
  attributeTypeMap: {},
  resourceDefined: [],
  attributeTypeShowRelateList: []
}
const mutations = {
  attributeType: (state, attributeType) => {
    state.attributeType = attributeType
  },
  attributeTypeShowRelateList: (state, attributeTypeShowRelateList) => {
    state.attributeTypeShowRelateList = attributeTypeShowRelateList
  },
  resourceDefinedList: (state, resourceDefinedList) => {
    state.resourceDefinedList = resourceDefinedList
  }
}
const actions = {
  loadAttributeType({ commit }) {
    getAttributeType()
      .then(
        res => {
          const res2 = []
          res.forEach(
            item => {
              if (item.relate === true) {
                res2.push(item.name)
              }
            }
          )
          commit('attributeType', res)
          commit('attributeTypeShowRelateList', res2)
        }
      )
  },
  loadResourceDefined({ commit }) {
    getResourceDefined({ limit: 0 })
      .then(
        res => {
          const res2 = []
          res.forEach(
            item => {
              res2.push({ id: item.id, name: item.name })
            }
          )
          commit('resourceDefinedList', res2)
        }
      )
  }
}

export default {
  namespaced: true,
  state,
  mutations,
  actions
}
