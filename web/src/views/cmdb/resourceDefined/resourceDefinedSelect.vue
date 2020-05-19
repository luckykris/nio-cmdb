<template>
  <el-select
    v-model="mySelectId"
    :remote-method="remoteMethod"
    remote
    placeholder="选择模型"
    reserve-keyword
    filterable
  >
    <el-option
      v-for="item in options"
      :key="item.id"
      :label="item.name"
      :value="item[index]"
    />
  </el-select>
</template>

<script>
import { getResourceDefined } from '@/api/resource'
export default {
  name: 'ResourceDefinedSelect',
  model: {
    prop: 'selectId',
    event: 'change'
  },
  props: {
    selectId: { type: String, default: null },
    index: { type: String, default: 'id' }
  },
  data() {
    return {
      options: [],
      loading: true,
      mySelectId: this.selectId
    }
  },
  watch: {
    mySelectId: {
      handler(cur, old) {
        this.$emit('change', cur)
      }
    }
  },
  methods: {
    remoteMethod(query) {
      getResourceDefined({ search: query }).then(
        (response) => {
          this.options = response.items
          this.loading = false
        }
      ).catch(
        (e) => {
          console.log(e)
          this.options = []
        }
      )
    },
    getObject() {
      for (let i = 0; i < this.options.length; i++) {
        if (this.options[i][this.index] === this.mySelectId) {
          return this.options[i]
        }
      }
    }
  }
}
</script>

<style scoped>

</style>
